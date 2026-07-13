from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Question, Quiz, QuizAttempt


class QuestionSerializer(serializers.ModelSerializer):
    # Optional on input: when creating via /quizzes/<id>/questions/ the quiz comes
    # from the URL, so the client should not have to repeat it in the body.
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(), required=False)
    order = serializers.IntegerField(required=False, min_value=1)
    # Declared explicitly rather than inheriting the model's ChoiceField, whose
    # to_internal_value() would reject a lower-case "a" before it can be normalised.
    correct_option = serializers.CharField(max_length=1)

    class Meta:
        model = Question
        fields = [
            "id",
            "quiz",
            "prompt",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_option",
            "explanation",
            "order",
        ]

    def validate_correct_option(self, value):
        value = str(value).strip().upper()
        if value not in {"A", "B", "C", "D"}:
            raise serializers.ValidationError("correct_option must be one of A, B, C or D.")
        return value

    def validate(self, attrs):
        # The flat /questions/ endpoint has no quiz in the URL, so it must be in the body.
        if self.instance is None and not attrs.get("quiz") and not self.context.get("quiz_from_url"):
            raise serializers.ValidationError({"quiz": "This field is required."})
        return attrs


class StudentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "prompt",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "order",
        ]


class QuizSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source="created_by.username", read_only=True, default=None)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "difficulty",
            "duration_minutes",
            "is_active",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
            "question_count",
        ]
        read_only_fields = ["created_by"]

    def get_question_count(self, obj):
        # QuizViewSet annotates this; fall back to a query for un-annotated instances
        # (e.g. the freshly created quiz returned by the AI generate endpoint).
        annotated = getattr(obj, "question_count", None)
        return annotated if annotated is not None else obj.questions.count()


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "quiz",
            "quiz_title",
            "student",
            "student_name",
            "responses",
            "score",
            "total",
            "percentage",
            "created_at",
        ]
        read_only_fields = ["student", "student_name", "score", "total"]


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=["teacher", "student"])

    def validate_username(self, value):
        value = value.strip()
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_password(self, value):
        # Run Django's configured AUTH_PASSWORD_VALIDATORS so the API enforces the
        # same password policy the admin site does.
        validate_password(value)
        return value

    def create(self, validated_data):
        role = validated_data.pop("role")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
