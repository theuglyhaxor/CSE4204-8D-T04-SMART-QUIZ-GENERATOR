from django.conf import settings
from django.contrib.auth import authenticate
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Question, Quiz, QuizAttempt
from .pdf import quiz_to_dict, render_quiz_pdf
from .permissions import IsStudentUser, IsTeacherOrStudentUser, IsTeacherUser, get_user_role
from .serializers import (
    LoginSerializer,
    QuestionSerializer,
    QuizAttemptSerializer,
    QuizSerializer,
    RegisterSerializer,
    StudentQuestionSerializer,
)
from ai_integration import extract_text_from_uploaded_file, generate_quiz


def get_tokens_for_user(user, role):
    """Issue a JWT refresh/access pair, embedding the user's role as a claim."""
    refresh = RefreshToken.for_user(user)
    refresh["role"] = role
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


def _user_payload(user, role):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": role,
    }


class MetaView(APIView):
    """Project/team identity — lets the frontend render the same footer as the PDF."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(settings.TEAM)


class AuthRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        role = get_user_role(user) or "student"
        return Response(
            {**get_tokens_for_user(user, role), "user": _user_payload(user, role)},
            status=status.HTTP_201_CREATED,
        )


class AuthLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request=request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        role = get_user_role(user) or "student"
        return Response({**get_tokens_for_user(user, role), "user": _user_payload(user, role)})


class AuthMeView(APIView):
    """Who am I? Used by the frontend to restore a session from a stored token."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_user_payload(request.user, get_user_role(request.user) or "student"))


class AuthLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # JWTs are stateless; "logout" means blacklisting the refresh token so it
        # can no longer be used to mint new access tokens.
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"detail": "Provide the 'refresh' token to invalidate."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class DocumentParseView(APIView):
    permission_classes = [IsTeacherUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded_file = request.FILES.get("file")
        if uploaded_file is None:
            return Response(
                {"detail": "Provide a file upload field named 'file'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            parsed = extract_text_from_uploaded_file(uploaded_file)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        parsed["word_count"] = len(parsed["text"].split())
        return Response(parsed)


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsTeacherUser()]
        return [IsTeacherOrStudentUser()]

    def get_queryset(self):
        queryset = (
            Quiz.objects.annotate(question_count=Count("questions"))
            .select_related("created_by")
        )
        # Students only ever see quizzes that have been activated.
        if get_user_role(self.request.user) == "student":
            queryset = queryset.filter(is_active=True)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def _assert_owner(self, quiz):
        # A teacher may only mutate quizzes they created. Legacy rows with no owner
        # stay editable so seeded databases don't become read-only.
        if quiz.created_by_id and quiz.created_by_id != self.request.user.id:
            raise PermissionDenied("You can only modify quizzes you created.")

    def perform_update(self, serializer):
        self._assert_owner(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self._assert_owner(instance)
        instance.delete()


class QuizQuestionListCreateView(ListCreateAPIView):
    """Questions for one quiz. Teacher-only — includes the correct answers."""

    serializer_class = QuestionSerializer
    permission_classes = [IsTeacherUser]

    def get_serializer_context(self):
        # Tells QuestionSerializer the quiz comes from the URL, not the request body.
        return {**super().get_serializer_context(), "quiz_from_url": True}

    def get_queryset(self):
        quiz = get_object_or_404(Quiz, pk=self.kwargs["quiz_id"])
        return quiz.questions.select_related("quiz")

    def perform_create(self, serializer):
        quiz = get_object_or_404(Quiz, pk=self.kwargs["quiz_id"])
        if quiz.created_by_id and quiz.created_by_id != self.request.user.id:
            raise PermissionDenied("You can only add questions to quizzes you created.")
        # Default the order to the end of the quiz rather than colliding on 1.
        next_order = quiz.questions.count() + 1
        serializer.save(quiz=quiz, order=serializer.validated_data.get("order") or next_order)


class QuestionDetailViewSet(viewsets.ModelViewSet):
    """Flat question access, used by the Question Bank screen."""

    serializer_class = QuestionSerializer
    permission_classes = [IsTeacherUser]

    def get_queryset(self):
        queryset = Question.objects.select_related("quiz")
        quiz_id = self.request.query_params.get("quiz")
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)
        return queryset


class QuizStudentQuestionsView(APIView):
    """Questions with the answers stripped out — what a student sees while taking a quiz."""

    permission_classes = [IsTeacherOrStudentUser]

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        if get_user_role(request.user) == "student" and not quiz.is_active:
            raise PermissionDenied("This quiz is not currently active.")
        serializer = StudentQuestionSerializer(quiz.questions.all(), many=True)
        return Response(serializer.data)


class QuizExportPDFView(APIView):
    """
    Download a quiz as a PDF.

    ?answers=false renders a clean student handout (no correct-option highlight,
    no explanations, no answer key). Teachers get the answer key by default;
    students can only ever fetch the handout.
    """

    permission_classes = [IsTeacherOrStudentUser]

    def get(self, request, quiz_id):
        quiz = get_object_or_404(
            Quiz.objects.prefetch_related("questions"), pk=quiz_id
        )
        role = get_user_role(request.user)

        if role == "student" and not quiz.is_active:
            raise PermissionDenied("This quiz is not currently active.")

        wants_answers = request.query_params.get("answers", "true").lower() != "false"
        include_answers = wants_answers and role == "teacher"

        pdf_bytes = render_quiz_pdf(
            quiz_to_dict(quiz),
            {
                "difficulty": quiz.difficulty,
                "duration_minutes": quiz.duration_minutes,
                "generated_on": quiz.created_at.date().isoformat(),
            },
            include_answers=include_answers,
        )

        slug = "".join(c if c.isalnum() else "_" for c in quiz.title).strip("_")[:50] or "quiz"
        suffix = "answer_key" if include_answers else "handout"

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{slug}_{suffix}.pdf"'
        return response


class AIGenerateQuizView(APIView):
    """Generate a quiz with the configured AI provider and persist it."""

    permission_classes = [IsTeacherUser]

    def post(self, request):
        title = request.data.get("title") or "AI Generated Quiz"

        try:
            question_count = int(request.data.get("question_count", 5))
            duration_minutes = int(request.data.get("duration_minutes", 5))
        except (TypeError, ValueError):
            return Response(
                {"detail": "question_count and duration_minutes must be integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if question_count < 1 or question_count > 50:
            return Response(
                {"detail": "question_count must be between 1 and 50."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if duration_minutes < 1:
            return Response(
                {"detail": "duration_minutes must be at least 1."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        difficulty = request.data.get("difficulty", "Medium")
        provider = request.data.get("provider")

        try:
            generated = generate_quiz(request.data, provider=provider)
        except RuntimeError as exc:
            # Missing API key / provider unreachable.
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if len(generated["questions"]) < question_count:
            return Response(
                {
                    "detail": (
                        f"The AI provider returned {len(generated['questions'])} questions "
                        f"but {question_count} were requested. Please try again."
                    )
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        quiz = Quiz.objects.create(
            title=generated["title"] or title,
            description=request.data.get("instruction") or "AI generated quiz.",
            difficulty=difficulty,
            duration_minutes=duration_minutes,
            created_by=request.user,
        )

        questions = [
            Question.objects.create(
                quiz=quiz,
                prompt=question["prompt"],
                option_a=question["option_a"],
                option_b=question["option_b"],
                option_c=question["option_c"],
                option_d=question["option_d"],
                correct_option=question["correct_option"],
                explanation=question["explanation"],
                order=order,
            )
            for order, question in enumerate(generated["questions"][:question_count], start=1)
        ]

        return Response(
            {
                "quiz": QuizSerializer(quiz).data,
                "questions": QuestionSerializer(questions, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )


class QuizSubmitView(APIView):
    """Score a student's answers and record the attempt against their account."""

    permission_classes = [IsStudentUser]

    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz.objects.prefetch_related("questions"), pk=quiz_id)

        if not quiz.is_active:
            raise PermissionDenied("This quiz is not currently active.")

        answers = request.data.get("answers", [])
        if not isinstance(answers, list) or not answers:
            return Response(
                {"detail": "Provide a non-empty answers list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        questions = {question.id: question for question in quiz.questions.all()}
        if not questions:
            return Response(
                {"detail": "This quiz has no questions yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        score = 0
        responses = []
        seen = set()

        for answer in answers:
            if not isinstance(answer, dict):
                return Response(
                    {"detail": "Each answer must be an object with 'question' and 'selected_option'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            question_id = answer.get("question")
            selected_option = str(answer.get("selected_option") or "").strip().upper()

            question = questions.get(question_id)
            if question is None:
                return Response(
                    {"detail": f"Question {question_id} does not belong to quiz {quiz_id}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if selected_option not in {"A", "B", "C", "D"}:
                return Response(
                    {"detail": f"selected_option for question {question_id} must be A, B, C or D."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if question_id in seen:
                return Response(
                    {"detail": f"Question {question_id} was answered more than once."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            seen.add(question_id)

            is_correct = selected_option == question.correct_option
            score += int(is_correct)

            responses.append(
                {
                    "question": question_id,
                    "selected_option": selected_option,
                    "correct_option": question.correct_option,
                    "is_correct": is_correct,
                    "explanation": question.explanation,
                }
            )

        # The attempt is attributed to the authenticated user, never to a name
        # supplied in the request body.
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=request.user,
            student_name=request.user.get_full_name() or request.user.username,
            responses=responses,
            score=score,
            total=len(questions),
        )

        return Response(
            {
                "attempt_id": attempt.id,
                "quiz": quiz.id,
                "quiz_title": quiz.title,
                "student_name": attempt.student_name,
                "score": attempt.score,
                "total": attempt.total,
                "percentage": attempt.percentage,
                "responses": attempt.responses,
            },
            status=status.HTTP_201_CREATED,
        )


class QuizAttemptListView(ListAPIView):
    """Every attempt at one quiz. Teacher-only — this is other students' data."""

    serializer_class = QuizAttemptSerializer
    permission_classes = [IsTeacherUser]

    def get_queryset(self):
        quiz = get_object_or_404(Quiz, pk=self.kwargs["quiz_id"])
        return quiz.attempts.select_related("quiz", "student")


class MyAttemptListView(ListAPIView):
    """A student's own attempt history."""

    serializer_class = QuizAttemptSerializer
    permission_classes = [IsStudentUser]

    def get_queryset(self):
        return QuizAttempt.objects.filter(student=self.request.user).select_related("quiz", "student")


class StatsView(APIView):
    """Dashboard counters. Shape depends on the caller's role."""

    permission_classes = [IsTeacherOrStudentUser]

    def get(self, request):
        role = get_user_role(request.user)

        if role == "teacher":
            quizzes = Quiz.objects.filter(created_by=request.user)
            attempts = QuizAttempt.objects.filter(quiz__created_by=request.user)
            scored = [a.percentage for a in attempts]
            return Response(
                {
                    "role": "teacher",
                    "total_quizzes": quizzes.count(),
                    "active_quizzes": quizzes.filter(is_active=True).count(),
                    "total_questions": Question.objects.filter(quiz__created_by=request.user).count(),
                    "total_attempts": attempts.count(),
                    "average_score": round(sum(scored) / len(scored), 2) if scored else 0.0,
                }
            )

        attempts = QuizAttempt.objects.filter(student=request.user)
        scored = [a.percentage for a in attempts]
        return Response(
            {
                "role": "student",
                "available_quizzes": Quiz.objects.filter(is_active=True).count(),
                "quizzes_taken": attempts.values("quiz").distinct().count(),
                "total_attempts": attempts.count(),
                "average_score": round(sum(scored) / len(scored), 2) if scored else 0.0,
                "best_score": round(max(scored), 2) if scored else 0.0,
            }
        )
