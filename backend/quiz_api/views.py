from django.contrib.auth import authenticate
from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Question, Quiz, QuizAttempt
from .permissions import IsStudentUser, IsTeacherOrStudentUser, IsTeacherUser
from .serializers import (
    LoginSerializer,
    QuestionSerializer,
    QuizAttemptSerializer,
    QuizSerializer,
    RegisterSerializer,
    StudentQuestionSerializer,
)
from .services import extract_text_from_uploaded_file, generate_quiz_with_gemini


class AuthRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        role = user.groups.first().name if user.groups.exists() else "student"
        return Response(
            {
                "token": token.key,
                "user": {"id": user.id, "username": user.username, "role": role},
            },
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
            return Response({"detail": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        role = user.groups.first().name if user.groups.exists() else "student"
        return Response(
            {
                "token": token.key,
                "user": {"id": user.id, "username": user.username, "role": role},
            }
        )


class DocumentParseView(APIView):
    permission_classes = [IsTeacherUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded_file = request.FILES.get("file")
        if uploaded_file is None:
            return Response({"detail": "Provide a file upload field named 'file'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            parsed = extract_text_from_uploaded_file(uploaded_file)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        parsed["word_count"] = len(parsed["text"].split())
        return Response(parsed)


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.annotate(question_count=Count("questions")).all()
    serializer_class = QuizSerializer

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsTeacherUser()]
        return [IsTeacherOrStudentUser()]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related("quiz").all()
    serializer_class = QuestionSerializer
    permission_classes = [IsTeacherUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        quiz_id = self.request.query_params.get("quiz")
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)
        return queryset


class QuizQuestionListCreateView(ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [IsTeacherUser]

    def get_queryset(self):
        quiz_id = self.kwargs.get("quiz_id")
        return Question.objects.filter(quiz_id=quiz_id).select_related("quiz")

    def perform_create(self, serializer):
        quiz_id = self.kwargs.get("quiz_id")
        quiz = Quiz.objects.get(pk=quiz_id)
        serializer.save(quiz=quiz)


class QuizStudentQuestionsView(APIView):
    permission_classes = [IsTeacherOrStudentUser]

    def get(self, request, quiz_id):
        quiz = Quiz.objects.get(pk=quiz_id)
        questions = quiz.questions.select_related("quiz")
        serializer = StudentQuestionSerializer(questions, many=True)
        return Response(serializer.data)


class GeminiGenerateQuizView(APIView):
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

        difficulty = request.data.get("difficulty", "Medium")

        if question_count < 1:
            return Response({"detail": "question_count must be at least 1."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            generated = generate_quiz_with_gemini(request.data)
        except RuntimeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if len(generated["questions"]) < question_count:
            return Response(
                {"detail": "Gemini did not return the requested number of questions."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        quiz = Quiz.objects.create(
            title=generated["title"] or title,
            description=request.data.get("instruction", "Generated by Gemini."),
            difficulty=difficulty,
            duration_minutes=duration_minutes,
        )

        questions = []
        for order, question in enumerate(generated["questions"][:question_count], start=1):
            question_obj = Question.objects.create(
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
            questions.append(question_obj)

        return Response(
            {
                "quiz": QuizSerializer(quiz).data,
                "questions": QuestionSerializer(questions, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )


class QuizSubmitView(APIView):
    permission_classes = [IsStudentUser]

    def post(self, request, quiz_id):
        quiz = Quiz.objects.get(pk=quiz_id)
        answers = request.data.get("answers", [])

        if not isinstance(answers, list) or not answers:
            return Response(
                {"detail": "Provide a non-empty answers list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        questions = list(quiz.questions.all())
        question_ids = {question.id for question in questions}
        score = 0
        responses = []

        for answer in answers:
            question_id = answer.get("question")
            selected_option = answer.get("selected_option")

            if question_id not in question_ids or not selected_option:
                return Response(
                    {"detail": "Each answer must include a valid question id and selected_option."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            question = next((item for item in questions if item.id == question_id), None)
            if question is None:
                return Response(
                    {"detail": f"Question {question_id} does not belong to quiz {quiz_id}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            is_correct = selected_option.upper() == question.correct_option
            if is_correct:
                score += 1

            responses.append(
                {
                    "question": question_id,
                    "selected_option": selected_option.upper(),
                    "correct_option": question.correct_option,
                    "is_correct": is_correct,
                }
            )

        total = len(questions)
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student_name=request.data.get("student_name", "Anonymous"),
            responses=responses,
            score=score,
            total=total,
        )

        return Response(
            {
                "quiz": quiz.id,
                "student_name": attempt.student_name,
                "score": attempt.score,
                "total": attempt.total,
                "percentage": round((attempt.score / attempt.total) * 100, 2) if attempt.total else 0,
                "responses": attempt.responses,
                "attempt_id": attempt.id,
            },
            status=status.HTTP_201_CREATED,
        )


class QuizAttemptListView(ListCreateAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsTeacherUser]

    def get_queryset(self):
        quiz_id = self.kwargs.get("quiz_id")
        return QuizAttempt.objects.filter(quiz_id=quiz_id)
