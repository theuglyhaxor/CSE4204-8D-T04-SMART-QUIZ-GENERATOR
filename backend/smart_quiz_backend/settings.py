import os
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