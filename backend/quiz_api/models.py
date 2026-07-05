from django.db import models


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=50, default="Medium")
    duration_minutes = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

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
    student_name = models.CharField(max_length=255, blank=True, default="Anonymous")
    responses = models.JSONField(default=list, blank=True)
    score = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student_name} - {self.quiz.title}"
