import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthRbacAndUploadAPITests(APITestCase):
    def create_user(self, username, password, role):
        response = self.client.post(
            reverse("auth-register"),
            {"username": username, "password": password, "role": role},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        return token

    def test_auth_rbac_flow_and_upload(self):
        suffix = uuid.uuid4().hex[:8]
        teacher_username = f"teacher_{suffix}"
        student_username = f"student_{suffix}"
        password = "Test@123"

        teacher_token = self.create_user(teacher_username, password, "teacher")
        student_token = self.create_user(student_username, password, "student")

        self.client.credentials()
        unauthenticated = self.client.get(reverse("quiz-list"))
        self.assertEqual(unauthenticated.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {teacher_token}")
        quiz_payload = {
            "title": "RBAC test quiz",
            "description": "Created by teacher",
            "difficulty": "Easy",
            "duration_minutes": 5,
        }
        quiz_response = self.client.post(reverse("quiz-list"), quiz_payload, format="json")
        self.assertEqual(quiz_response.status_code, status.HTTP_201_CREATED)
        quiz_id = quiz_response.data["id"]

        question_payload = {
            "quiz": quiz_id,
            "prompt": "What is 2 + 2?",
            "option_a": "3",
            "option_b": "4",
            "option_c": "5",
            "option_d": "6",
            "correct_option": "B",
            "explanation": "Two plus two equals four.",
            "order": 1,
        }
        question_response = self.client.post(reverse("question-list"), question_payload, format="json")
        self.assertEqual(question_response.status_code, status.HTTP_201_CREATED)
        question_id = question_response.data["id"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {student_token}")
        student_questions = self.client.get(reverse("quiz-student-questions", kwargs={"quiz_id": quiz_id}))
        self.assertEqual(student_questions.status_code, status.HTTP_200_OK)
        self.assertEqual(student_questions.data[0]["id"], question_id)
        self.assertNotIn("correct_option", student_questions.data[0])

        submit_response = self.client.post(
            reverse("quiz-submit", kwargs={"quiz_id": quiz_id}),
            {"student_name": student_username, "answers": [{"question": question_id, "selected_option": "B"}]},
            format="json",
        )
        self.assertEqual(submit_response.status_code, status.HTTP_201_CREATED)

        student_ai = self.client.post(
            reverse("ai-generate-quiz"),
            {"title": "Should fail", "question_count": 2, "duration_minutes": 5},
            format="json",
        )
        self.assertEqual(student_ai.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {teacher_token}")
        upload = SimpleUploadedFile("notes.txt", b"Alpha\nBeta", content_type="text/plain")
        upload_response = self.client.post(
            reverse("document-parse"),
            {"file": upload},
            format="multipart",
        )
        self.assertEqual(upload_response.status_code, status.HTTP_200_OK)
        self.assertEqual(upload_response.data["filename"], "notes.txt")
        self.assertIn("Alpha", upload_response.data["text"])
        self.assertIn("Beta", upload_response.data["text"])
