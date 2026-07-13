from django.contrib.auth.models import User
from django.db import models


class Quiz(models.Model):
    DIFFICULTIES = (
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=50, choices=DIFFICULTIES, default="Medium")
    duration_minutes = models.PositiveIntegerField(default=5)
    # New quizzes start as drafts. Defaulting to active published an empty quiz to
    # students the instant it was created, before any questions existed.
    is_active = models.BooleanField(default=False)
    # Null for the pre-ownership rows that already exist in seeded databases.
    created_by = models.ForeignKey(
        User,
        related_name="quizzes",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "quizzes"

    def __str__(self):
        return self.title


class Question(models.Model):
    CORRECT_OPTIONS = (
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    )

    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.CASCADE)
    prompt = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=CORRECT_OPTIONS)
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, related_name="attempts", on_delete=models.CASCADE)
    # The authenticated submitter. student_name is kept as a denormalised display
    # label (and for legacy rows), but the FK is what authorisation is checked against
    # — a student must never be able to attribute an attempt to someone else.
    student = models.ForeignKey(
        User,
        related_name="attempts",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    student_name = models.CharField(max_length=255, blank=True, default="Anonymous")
    responses = models.JSONField(default=list, blank=True)
    score = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student_name} - {self.quiz.title}"

    @property
    def percentage(self):
        return round((self.score / self.total) * 100, 2) if self.total else 0.0
