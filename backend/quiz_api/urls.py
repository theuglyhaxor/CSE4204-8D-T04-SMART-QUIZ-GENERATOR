from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AIGenerateQuizView,
    AuthLoginView,
    AuthLogoutView,
    AuthMeView,
    AuthRegisterView,
    DocumentParseView,
    MetaView,
    MyAttemptListView,
    QuestionDetailViewSet,
    QuizAttemptListView,
    QuizExportPDFView,
    QuizQuestionListCreateView,
    QuizStudentQuestionsView,
    QuizSubmitView,
    QuizViewSet,
    StatsView,
)

quiz_list = QuizViewSet.as_view({"get": "list", "post": "create"})
quiz_detail = QuizViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)
question_list = QuestionDetailViewSet.as_view({"get": "list", "post": "create"})
question_detail = QuestionDetailViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

urlpatterns = [
    # Meta
    path("meta/", MetaView.as_view(), name="meta"),
    path("stats/", StatsView.as_view(), name="stats"),
    # Auth
    path("auth/register/", AuthRegisterView.as_view(), name="auth-register"),
    path("auth/login/", AuthLoginView.as_view(), name="auth-login"),
    path("auth/logout/", AuthLogoutView.as_view(), name="auth-logout"),
    path("auth/me/", AuthMeView.as_view(), name="auth-me"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    # Quizzes
    path("quizzes/", quiz_list, name="quiz-list"),
    path("quizzes/<int:pk>/", quiz_detail, name="quiz-detail"),
    path("quizzes/<int:quiz_id>/questions/", QuizQuestionListCreateView.as_view(), name="quiz-questions"),
    path("quizzes/<int:quiz_id>/student-questions/", QuizStudentQuestionsView.as_view(), name="quiz-student-questions"),
    path("quizzes/<int:quiz_id>/export-pdf/", QuizExportPDFView.as_view(), name="quiz-export-pdf"),
    path("quizzes/<int:quiz_id>/submit/", QuizSubmitView.as_view(), name="quiz-submit"),
    path("quizzes/<int:quiz_id>/attempts/", QuizAttemptListView.as_view(), name="quiz-attempts"),
    # Questions (question bank)
    path("questions/", question_list, name="question-list"),
    path("questions/<int:pk>/", question_detail, name="question-detail"),
    # Attempts
    path("attempts/me/", MyAttemptListView.as_view(), name="my-attempts"),
    # Documents + AI
    path("documents/parse/", DocumentParseView.as_view(), name="document-parse"),
    path("ai/generate-quiz/", AIGenerateQuizView.as_view(), name="ai-generate-quiz"),
]
