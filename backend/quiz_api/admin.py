from django.contrib import admin

from .models import Question, Quiz, QuizAttempt


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "difficulty", "duration_minutes", "is_active", "created_at"]
    search_fields = ["title", "description"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["id", "quiz", "order", "correct_option"]
    list_filter = ["quiz", "correct_option"]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ["id", "quiz", "student_name", "score", "total", "created_at"]
    list_filter = ["quiz", "created_at"]
