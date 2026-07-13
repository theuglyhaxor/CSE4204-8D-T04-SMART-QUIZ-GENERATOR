"""
Generate sample quizzes with the app's AI integration and export them as PDFs so you
can review the quality of the generated questions.

It calls the SAME dispatcher the API uses (ai_integration.generate_quiz) and the SAME
renderer the download endpoint uses (quiz_api.pdf.render_quiz_pdf), so what you see in
the PDF is exactly what the application produces. Nothing is written to the database —
these are throwaway samples for review.

USAGE
    cd backend
    python ai_integration/generate_sample_quizzes_pdf.py

    # custom topics (one quiz per topic):
    python ai_integration/generate_sample_quizzes_pdf.py "Python basics" "World War II"

    # choose the provider (default: gemini, or whatever AI_PROVIDER is set to):
    python ai_integration/generate_sample_quizzes_pdf.py --provider claude "Quantum physics"

    # produce the student handout (no answer key / explanations):
    python ai_integration/generate_sample_quizzes_pdf.py --no-answers "Cell biology"

REQUIREMENTS
    - GEMINI_API_KEY (for gemini) or ANTHROPIC_API_KEY (for claude) in backend/.env

Output: PDFs are written to  backend/sample_quizzes/
"""

import os
import sys
import time

import django

# --- Django setup so .env (API keys) loads and we can import the app packages ---
HERE = os.path.dirname(os.path.abspath(__file__))   # .../backend/ai_integration
BASE = os.path.dirname(HERE)                        # .../backend
sys.path.insert(0, BASE)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smart_quiz_backend.settings")
django.setup()

from ai_integration import generate_quiz          # noqa: E402
from quiz_api.pdf import render_quiz_pdf          # noqa: E402

OUTPUT_DIR = os.path.join(BASE, "sample_quizzes")

# (topic, difficulty, question_count). Kept small so the free-tier rate limit is happy.
DEFAULT_QUIZZES = [
    ("Photosynthesis and plant biology", "Easy", 5),
    ("Python programming fundamentals", "Medium", 5),
    ("World geography: capitals and rivers", "Hard", 5),
]

TRANSIENT = ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "high demand", "overloaded")


def _parse_args(argv):
    """Pull the optional flags out; whatever is left are topics."""
    args = list(argv)

    include_answers = True
    if "--no-answers" in args:
        args.remove("--no-answers")
        include_answers = False

    provider = None
    if "--provider" in args:
        i = args.index("--provider")
        if i + 1 < len(args):
            provider = args[i + 1]
            del args[i:i + 2]
        else:
            del args[i]

    return provider, include_answers, args


def _generate_with_retry(payload, provider, attempts=4):
    """Retry on transient errors (rate-limit 429 / overload 503) with backoff."""
    last = None
    for attempt in range(1, attempts + 1):
        try:
            return generate_quiz(payload, provider=provider)
        except (RuntimeError, ValueError) as exc:
            last = exc
            transient = any(token in str(exc) for token in TRANSIENT)
            # A ValueError here is usually a truncated/garbled JSON parse — a fresh
            # call often succeeds, so retry those too.
            if (transient or isinstance(exc, ValueError)) and attempt < attempts:
                wait = 15 * attempt
                reason = "model busy/limited" if transient else "bad response, retrying"
                print(f"      {reason}; retrying in {wait}s (attempt {attempt}/{attempts})...")
                time.sleep(wait)
                continue
            raise
    raise last


def main():
    provider, include_answers, topics = _parse_args(sys.argv[1:])
    provider = (provider or os.environ.get("AI_PROVIDER") or "gemini").strip().lower()

    if provider in {"claude", "anthropic"}:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("ERROR: ANTHROPIC_API_KEY is not set. Add it to backend/.env and retry.")
            sys.exit(1)
        model = os.environ.get("CLAUDE_MODEL", "claude-opus-4-8")
    else:
        if not os.environ.get("GEMINI_API_KEY"):
            print("ERROR: GEMINI_API_KEY is not set. Add it to backend/.env and retry.")
            sys.exit(1)
        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # CLI topics override the defaults (one quiz per topic, Hard / 5 questions).
    quizzes = [(topic, "Hard", 5) for topic in topics] if topics else DEFAULT_QUIZZES

    variant = "with answer key" if include_answers else "student handout"
    print(f"Generating {len(quizzes)} sample quiz(zes) with '{provider}' (model '{model}', {variant})...")
    print(f"Output folder: {OUTPUT_DIR}\n")

    generated = 0
    for i, (topic, difficulty, count) in enumerate(quizzes, start=1):
        print(f"[{i}/{len(quizzes)}] {topic}  ({difficulty}, {count} questions)")
        try:
            quiz = _generate_with_retry(
                {
                    "topic": topic,
                    "difficulty": difficulty,
                    "question_count": count,
                    "instruction": "Make the questions clear, factual, and unambiguous.",
                },
                provider,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"      FAILED: {exc}\n")
            continue

        pdf_bytes = render_quiz_pdf(
            quiz,
            {"difficulty": difficulty, "duration_minutes": count * 2, "model": model},
            include_answers=include_answers,
        )

        safe_name = "".join(c if c.isalnum() else "_" for c in topic).strip("_")[:40]
        path = os.path.join(OUTPUT_DIR, f"{i:02d}_{safe_name}.pdf")
        with open(path, "wb") as handle:
            handle.write(pdf_bytes)

        generated += 1
        print(f'      OK -> {os.path.relpath(path)}  ("{quiz["title"]}", {len(quiz["questions"])} questions)\n')

        # Be gentle with the free-tier per-minute limit.
        if i < len(quizzes):
            time.sleep(4)

    print("=" * 60)
    print(f"Done. {generated}/{len(quizzes)} quiz PDFs written to {OUTPUT_DIR}")
    if generated:
        print("Open the PDFs to review question quality, options, and explanations.")


if __name__ == "__main__":
    main()
