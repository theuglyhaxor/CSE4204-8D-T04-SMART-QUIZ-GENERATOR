import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-secret-key-change-me"
)

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = [
    host
    for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost"
    ).split(",")
    if host
]

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# AI provider selection. Default stays "gemini" so existing behaviour is unchanged.
# Set AI_PROVIDER=claude (or pass "provider": "claude" per request) to use Claude.
AI_PROVIDER = os.environ.get("AI_PROVIDER", "gemini")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "quiz_api",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "smart_quiz_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "smart_quiz_backend.wsgi.application"

# --- Database -----------------------------------------------------------------
# DB_ENGINE picks the backend:
#   sqlite (default) -> zero-setup file DB, so `manage.py runserver` works on a
#                       clean clone with no XAMPP/MySQL running.
#   mysql            -> the MySQL/MariaDB deployment described in database/schema.sql.
DB_ENGINE = os.environ.get("DB_ENGINE", "sqlite").strip().lower()

if DB_ENGINE in {"mysql", "mariadb"}:
    import pymysql

    pymysql.install_as_MySQLdb()

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("DB_NAME", "smart_quiz_generator"),
            "USER": os.environ.get("DB_USER", "root"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
            "PORT": os.environ.get("DB_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / os.environ.get("DB_NAME", "smart_quiz.sqlite3"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# JSON Web Token (JWT) configuration — djangorestframework-simplejwt.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# The Vite dev server (frontend/) runs on 5173 — it must be allowed or the browser
# blocks every API call. Override with CORS_ALLOWED_ORIGINS for other origins.
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    ).split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

# --- Team identity ------------------------------------------------------------
# Single source of truth for the footer stamped onto every exported quiz PDF and
# surfaced at GET /api/meta/. Keeping it here means the identity is edited in one
# place rather than in each template.
TEAM = {
    "course": "CSE4204 — Mobile Computing Lab",
    "team_id": "CSE4204-8D-T04",
    "section": "8D",
    "team": "T04",
    "project": "Smart Quiz Generator",
    "department": "Department of Computer Science and Engineering",
    "university": "Northern University of Business and Technology, Khulna",
    "repo": "https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR",
    "members": [
        {"name": "MD Rohan", "student_id": "11220320958", "role": "Backend Developer, Full Stack"},
        {"name": "Sharmin Nahar Tumpa", "student_id": "11220320962", "role": "AI Integration"},
        {"name": "Pial Tarofdar", "student_id": "11220320965", "role": "Frontend Developer"},
        {"name": "Sanjana Athoy", "student_id": "11220320953", "role": "Technical Support"},
    ],
}
