from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AuthLoginView,
    AuthLogoutView,
    AuthRegisterView,
    DocumentParseView,
    GeminiGenerateQuizView,
    QuestionViewSet,
    QuizAttemptListView,
    QuizQuestionListCreateView,
    QuizStudentQuestionsView,
    QuizSubmitView,
    QuizViewSet,
)

urlpatterns = [
    path("auth/register/", AuthRegisterView.as_view(), name="auth-register"),
    path("auth/login/", AuthLoginView.as_view(), name="auth-login"),
    path("auth/logout/", AuthLogoutView.as_view(), name="auth-logout"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("quizzes/", QuizViewSet.as_view({"get": "list", "post": "create"}), name="quiz-list"),
    path("quizzes/<int:pk>/", QuizViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}), name="quiz-detail"),
    path("quizzes/<int:quiz_id>/questions/", QuizQuestionListCreateView.as_view(), name="quiz-questions"),
    path("quizzes/<int:quiz_id>/student-questions/", QuizStudentQuestionsView.as_view(), name="quiz-student-questions"),
    path("quizzes/<int:quiz_id>/submit/", QuizSubmitView.as_view(), name="quiz-submit"),
    path("quizzes/<int:quiz_id>/attempts/", QuizAttemptListView.as_view(), name="quiz-attempts"),
    path("questions/", QuestionViewSet.as_view({"get": "list", "post": "create"}), name="question-list"),
    path("questions/<int:pk>/", QuestionViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}), name="question-detail"),
    path("documents/parse/", DocumentParseView.as_view(), name="document-parse"),
    path("ai/generate-quiz/", GeminiGenerateQuizView.as_view(), name="ai-generate-quiz"),
]
