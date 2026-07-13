"""
End-to-end API tests for the Smart Quiz Generator.

Covers the teacher and student journeys, the role-based authorisation rules, and
the regressions that were fixed (404-not-500 on unknown ids, quiz ownership, and
attempts being attributed to the authenticated user rather than a name in the body).

    python manage.py test quiz_api
"""

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Question, Quiz, QuizAttempt

PASSWORD = "Str0ng!Pass123"


def make_user(username, role, password=PASSWORD):
    user = User.objects.create_user(username=username, password=password)
    group, _ = Group.objects.get_or_create(name=role)
    user.groups.add(group)
    return user


class ApiTestCase(APITestCase):
    def auth(self, username, password=PASSWORD):
        response = self.client.post(
            "/api/auth/login/", {"username": username, "password": password}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response.data


class AuthTests(ApiTestCase):
    def test_register_returns_jwt_pair_and_role(self):
        response = self.client.post(
            "/api/auth/register/",
            {"username": "teacher1", "password": PASSWORD, "role": "teacher"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["role"], "teacher")

    def test_duplicate_username_is_rejected(self):
        make_user("teacher1", "teacher")
        response = self.client.post(
            "/api/auth/register/",
            {"username": "teacher1", "password": PASSWORD, "role": "teacher"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_password_is_rejected(self):
        response = self.client.post(
            "/api/auth/register/",
            {"username": "teacher1", "password": "123", "role": "teacher"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_password_returns_401(self):
        make_user("teacher1", "teacher")
        response = self.client.post(
            "/api/auth/login/", {"username": "teacher1", "password": "nope"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_restores_a_session_from_a_stored_token(self):
        make_user("student1", "student")
        self.auth("student1")
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "student1")
        self.assertEqual(response.data["role"], "student")

    def test_protected_route_requires_a_token(self):
        self.assertEqual(self.client.get("/api/quizzes/").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_the_refresh_token(self):
        make_user("student1", "student")
        tokens = self.auth("student1")

        logout = self.client.post("/api/auth/logout/", {"refresh": tokens["refresh"]}, format="json")
        self.assertEqual(logout.status_code, status.HTTP_200_OK)

        self.client.credentials()
        refresh = self.client.post(
            "/api/auth/token/refresh/", {"refresh": tokens["refresh"]}, format="json"
        )
        self.assertEqual(refresh.status_code, status.HTTP_401_UNAUTHORIZED)


class QuizPermissionTests(ApiTestCase):
    def setUp(self):
        self.teacher = make_user("teacher1", "teacher")
        self.other_teacher = make_user("teacher2", "teacher")
        self.student = make_user("student1", "student")

    def test_student_cannot_create_a_quiz(self):
        self.auth("student1")
        response = self.client.post("/api/quizzes/", {"title": "Nope"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_creating_a_quiz_becomes_its_owner(self):
        self.auth("teacher1")
        response = self.client.post(
            "/api/quizzes/",
            {"title": "Algebra", "difficulty": "Easy", "duration_minutes": 10},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["created_by"], self.teacher.id)
        self.assertEqual(response.data["created_by_username"], "teacher1")

    def test_new_quiz_starts_as_a_draft(self):
        # Regression: is_active defaulted to True, so creating a quiz immediately
        # published it to students — before it had any questions.
        self.auth("teacher1")
        response = self.client.post("/api/quizzes/", {"title": "Fresh"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data["is_active"])

        self.auth("student1")
        self.assertEqual(self.client.get("/api/quizzes/").data, [])

    def test_teacher_cannot_delete_another_teachers_quiz(self):
        quiz = Quiz.objects.create(title="Mine", created_by=self.teacher)
        self.auth("teacher2")
        self.assertEqual(
            self.client.delete(f"/api/quizzes/{quiz.id}/").status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertTrue(Quiz.objects.filter(pk=quiz.id).exists())

    def test_students_only_see_active_quizzes(self):
        Quiz.objects.create(title="Live", is_active=True, created_by=self.teacher)
        Quiz.objects.create(title="Draft", is_active=False, created_by=self.teacher)

        self.auth("student1")
        self.assertEqual([q["title"] for q in self.client.get("/api/quizzes/").data], ["Live"])

        self.auth("teacher1")
        self.assertEqual(
            sorted(q["title"] for q in self.client.get("/api/quizzes/").data), ["Draft", "Live"]
        )

    def test_unknown_quiz_returns_404_not_500(self):
        # Regression: these views used an unguarded Quiz.objects.get(), so a bad id
        # raised DoesNotExist and surfaced to the client as a 500.
        self.auth("teacher1")
        for path in ("questions", "student-questions", "attempts", "export-pdf"):
            self.assertEqual(
                self.client.get(f"/api/quizzes/9999/{path}/").status_code,
                status.HTTP_404_NOT_FOUND,
                msg=f"/api/quizzes/9999/{path}/ should 404",
            )

        self.auth("student1")
        response = self.client.post(
            "/api/quizzes/9999/submit/",
            {"answers": [{"question": 1, "selected_option": "A"}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class QuizFlowTests(ApiTestCase):
    def setUp(self):
        self.teacher = make_user("teacher1", "teacher")
        self.student = make_user("student1", "student")
        self.quiz = Quiz.objects.create(
            title="Solar System", difficulty="Easy", duration_minutes=5,
            is_active=True, created_by=self.teacher,
        )
        self.q1 = Question.objects.create(
            quiz=self.quiz, prompt="Largest planet?",
            option_a="Earth", option_b="Jupiter", option_c="Mars", option_d="Venus",
            correct_option="B", explanation="Jupiter is the largest.", order=1,
        )
        self.q2 = Question.objects.create(
            quiz=self.quiz, prompt="Closest planet to the Sun?",
            option_a="Mercury", option_b="Venus", option_c="Earth", option_d="Mars",
            correct_option="A", explanation="Mercury is closest.", order=2,
        )

    def test_question_creation_defaults_order_to_the_end_and_normalises_the_option(self):
        self.auth("teacher1")
        response = self.client.post(
            f"/api/quizzes/{self.quiz.id}/questions/",
            {
                "prompt": "Which planet has rings?",
                "option_a": "Saturn", "option_b": "Earth", "option_c": "Mars", "option_d": "Venus",
                "correct_option": "a",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["order"], 3)
        self.assertEqual(response.data["correct_option"], "A")

    def test_student_questions_hide_the_answers(self):
        self.auth("student1")
        response = self.client.get(f"/api/quizzes/{self.quiz.id}/student-questions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for question in response.data:
            self.assertNotIn("correct_option", question)
            self.assertNotIn("explanation", question)

    def test_submit_scores_and_binds_the_attempt_to_the_logged_in_student(self):
        self.auth("student1")
        response = self.client.post(
            f"/api/quizzes/{self.quiz.id}/submit/",
            {
                "student_name": "Somebody Else",  # spoof attempt — must be ignored
                "answers": [
                    {"question": self.q1.id, "selected_option": "B"},  # correct
                    {"question": self.q2.id, "selected_option": "C"},  # wrong
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["score"], 1)
        self.assertEqual(response.data["total"], 2)
        self.assertEqual(response.data["percentage"], 50.0)

        attempt = QuizAttempt.objects.get(pk=response.data["attempt_id"])
        self.assertEqual(attempt.student, self.student)
        self.assertEqual(attempt.student_name, "student1")

    def test_submit_rejects_a_question_from_another_quiz(self):
        other = Quiz.objects.create(title="Other", created_by=self.teacher)
        foreign = Question.objects.create(
            quiz=other, prompt="?", option_a="a", option_b="b", option_c="c", option_d="d",
            correct_option="A",
        )
        self.auth("student1")
        response = self.client.post(
            f"/api/quizzes/{self.quiz.id}/submit/",
            {"answers": [{"question": foreign.id, "selected_option": "A"}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_rejects_an_invalid_option(self):
        self.auth("student1")
        response = self.client.post(
            f"/api/quizzes/{self.quiz.id}/submit/",
            {"answers": [{"question": self.q1.id, "selected_option": "Z"}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_rejects_a_duplicate_answer(self):
        self.auth("student1")
        response = self.client.post(
            f"/api/quizzes/{self.quiz.id}/submit/",
            {
                "answers": [
                    {"question": self.q1.id, "selected_option": "B"},
                    {"question": self.q1.id, "selected_option": "B"},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_is_blocked_on_an_inactive_quiz(self):
        self.quiz.is_active = False
        self.quiz.save()
        self.auth("student1")
        response = self.client.post(
            f"/api/quizzes/{self.quiz.id}/submit/",
            {"answers": [{"question": self.q1.id, "selected_option": "B"}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_cannot_submit(self):
        self.auth("teacher1")
        response = self.client.post(
            f"/api/quizzes/{self.quiz.id}/submit/",
            {"answers": [{"question": self.q1.id, "selected_option": "B"}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_read_the_class_attempt_list(self):
        self.auth("student1")
        response = self.client.get(f"/api/quizzes/{self.quiz.id}/attempts/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_sees_only_their_own_attempt_history(self):
        classmate = make_user("student2", "student")
        QuizAttempt.objects.create(quiz=self.quiz, student=self.student, score=2, total=2)
        QuizAttempt.objects.create(quiz=self.quiz, student=classmate, score=0, total=2)

        self.auth("student1")
        response = self.client.get("/api/attempts/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["student"], self.student.id)

    def test_teacher_sees_every_attempt_at_their_quiz(self):
        QuizAttempt.objects.create(quiz=self.quiz, student=self.student, score=2, total=2)
        self.auth("teacher1")
        response = self.client.get(f"/api/quizzes/{self.quiz.id}/attempts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["percentage"], 100.0)
        self.assertEqual(response.data[0]["quiz_title"], "Solar System")


class StatsTests(ApiTestCase):
    def setUp(self):
        self.teacher = make_user("teacher1", "teacher")
        self.student = make_user("student1", "student")
        self.quiz = Quiz.objects.create(title="Q", is_active=True, created_by=self.teacher)
        Question.objects.create(
            quiz=self.quiz, prompt="?", option_a="a", option_b="b", option_c="c", option_d="d",
            correct_option="A",
        )
        QuizAttempt.objects.create(quiz=self.quiz, student=self.student, score=1, total=2)

    def test_teacher_stats(self):
        self.auth("teacher1")
        data = self.client.get("/api/stats/").data
        self.assertEqual(data["role"], "teacher")
        self.assertEqual(data["total_quizzes"], 1)
        self.assertEqual(data["total_questions"], 1)
        self.assertEqual(data["total_attempts"], 1)
        self.assertEqual(data["average_score"], 50.0)

    def test_student_stats(self):
        self.auth("student1")
        data = self.client.get("/api/stats/").data
        self.assertEqual(data["role"], "student")
        self.assertEqual(data["available_quizzes"], 1)
        self.assertEqual(data["quizzes_taken"], 1)
        self.assertEqual(data["best_score"], 50.0)


class PDFExportTests(ApiTestCase):
    def setUp(self):
        self.teacher = make_user("teacher1", "teacher")
        self.student = make_user("student1", "student")
        self.quiz = Quiz.objects.create(
            # Curly quotes and an em-dash: these must not crash the renderer.
            title="Photosynthesis — the “Light” Reactions",
            description="Answer all questions.",
            difficulty="Hard", duration_minutes=20, is_active=True, created_by=self.teacher,
        )
        for i in range(3):
            Question.objects.create(
                quiz=self.quiz, prompt=f"Question {i + 1}?",
                option_a="Alpha", option_b="Beta", option_c="Gamma", option_d="Delta",
                correct_option="C", explanation="Because gamma.", order=i + 1,
            )

    def _body(self, response):
        return b"".join(response.streaming_content) if response.streaming else response.content

    def test_teacher_downloads_a_pdf_with_the_answer_key(self):
        self.auth("teacher1")
        response = self.client.get(f"/api/quizzes/{self.quiz.id}/export-pdf/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("answer_key", response["Content-Disposition"])

        body = self._body(response)
        self.assertTrue(body.startswith(b"%PDF-"))
        self.assertGreater(len(body), 1000)

    def test_student_export_is_always_the_handout_even_if_answers_are_requested(self):
        self.auth("student1")
        response = self.client.get(f"/api/quizzes/{self.quiz.id}/export-pdf/?answers=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("handout", response["Content-Disposition"])
        self.assertTrue(self._body(response).startswith(b"%PDF-"))

    def test_teacher_can_request_the_student_handout(self):
        self.auth("teacher1")
        response = self.client.get(f"/api/quizzes/{self.quiz.id}/export-pdf/?answers=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("handout", response["Content-Disposition"])


class DocumentParseTests(ApiTestCase):
    def setUp(self):
        make_user("teacher1", "teacher")
        make_user("student1", "student")

    def test_teacher_parses_an_uploaded_text_file(self):
        self.auth("teacher1")
        upload = SimpleUploadedFile("notes.txt", b"Alpha\nBeta", content_type="text/plain")
        response = self.client.post("/api/documents/parse/", {"file": upload}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["filename"], "notes.txt")
        self.assertIn("Alpha", response.data["text"])
        self.assertEqual(response.data["word_count"], 2)

    def test_student_cannot_parse_documents(self):
        self.auth("student1")
        upload = SimpleUploadedFile("notes.txt", b"Alpha", content_type="text/plain")
        response = self.client.post("/api/documents/parse/", {"file": upload}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MetaTests(ApiTestCase):
    def test_meta_exposes_the_team_identity(self):
        response = self.client.get("/api/meta/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["team_id"], "CSE4204-8D-T04")
        self.assertEqual(len(response.data["members"]), 4)
