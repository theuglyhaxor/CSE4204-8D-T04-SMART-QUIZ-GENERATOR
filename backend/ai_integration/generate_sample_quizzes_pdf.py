"""
Generate sample quizzes with the app's AI integration and export them as PDFs
so you can review the quality of the generated questions.

It calls the SAME dispatcher the API uses (ai_integration.generate_quiz), so what
you see in the PDF is exactly what the application produces. Nothing is written
to the database — these are throwaway samples for review.

USAGE
    cd backend
    python ai_integration/generate_sample_quizzes_pdf.py

    # custom topics (one quiz per topic):
    python ai_integration/generate_sample_quizzes_pdf.py "Python basics" "World War II"

    # choose the provider (default: gemini, or whatever AI_PROVIDER is set to):
    python ai_integration/generate_sample_quizzes_pdf.py --provider claude "Quantum physics"

REQUIREMENTS
    - GEMINI_API_KEY (for gemini) or ANTHROPIC_API_KEY (for claude) in backend/.env
    - fpdf2            ->  pip install fpdf2

Output: PDFs are written to  backend/sample_quizzes/
"""

import os
import sys
import time

import django
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# --- Django setup so .env (API keys) loads and we can import the AI package -----
HERE = os.path.dirname(os.path.abspath(__file__))   # .../backend/ai_integration
BASE = os.path.dirname(HERE)                          # .../backend
sys.path.insert(0, BASE)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smart_quiz_backend.settings")
django.setup()

from ai_integration import generate_quiz  # noqa: E402

OUTPUT_DIR = os.path.join(BASE, "sample_quizzes")

# (topic, difficulty, question_count). Kept small so the free-tier rate limit is happy.
DEFAULT_QUIZZES = [
    ("Photosynthesis and plant biology", "Easy", 5),
    ("Python programming fundamentals", "Medium", 5),
    ("World geography: capitals and rivers", "Hard", 5),
]

OPTION_LABELS = ["A", "B", "C", "D"]


# --------------------------------------------------------------------------- #
# Text sanitising — fpdf core fonts are latin-1 only, so map common unicode
# punctuation the models like to use down to plain ASCII.
# --------------------------------------------------------------------------- #
_REPLACEMENTS = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "…": "...", " ": " ",
    "•": "-", "→": "->", "°": " deg",
}


def clean(text):
    text = str(text)
    for bad, good in _REPLACEMENTS.items():
        text = text.replace(bad, good)
    # Drop anything still outside latin-1 so fpdf never crashes.
    return text.encode("latin-1", "replace").decode("latin-1")


# --------------------------------------------------------------------------- #
# PDF rendering
# --------------------------------------------------------------------------- #
class QuizPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150)
        self.cell(0, 8, clean(self._quiz_title), align="R")
        self.ln(10)
        self.set_text_color(0)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")
        self.set_text_color(0)


def render_quiz_pdf(quiz, meta, path):
    pdf = QuizPDF()
    pdf._quiz_title = quiz["title"]
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Title block
    pdf.set_font("Helvetica", "B", 18)
    pdf.multi_cell(0, 9, clean(quiz["title"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(90)
    pdf.cell(
        0, 6,
        clean(f"Topic: {meta['topic']}    |    Difficulty: {meta['difficulty']}    |    "
              f"Questions: {len(quiz['questions'])}    |    Model: {meta['model']}"),
    )
    pdf.ln(8)
    pdf.set_draw_color(200)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(4)
    pdf.set_text_color(0)

    # Questions
    for idx, q in enumerate(quiz["questions"], start=1):
        _question_block(pdf, idx, q)

    # Answer key
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 9, "Answer Key")
    pdf.ln(11)
    pdf.set_font("Helvetica", "", 11)
    for idx, q in enumerate(quiz["questions"], start=1):
        correct = q["correct_option"]
        correct_text = q[f"option_{correct.lower()}"]
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(14, 7, f"{idx}. {correct}")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, clean(correct_text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1)

    pdf.output(path)


def _question_block(pdf, idx, q):
    # Keep a question from splitting awkwardly across a page break if near bottom.
    if pdf.get_y() > pdf.h - 70:
        pdf.add_page()

    pdf.set_font("Helvetica", "B", 12)
    pdf.multi_cell(0, 7, clean(f"{idx}. {q['prompt']}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)

    pdf.set_font("Helvetica", "", 11)
    for label in OPTION_LABELS:
        option_text = q[f"option_{label.lower()}"]
        is_correct = label == q["correct_option"]
        if is_correct:
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(0, 120, 0)
            marker = "  (correct)"
        else:
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(0)
            marker = ""
        pdf.multi_cell(0, 6, clean(f"   {label}. {option_text}{marker}"),
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0)

    explanation = q.get("explanation", "").strip()
    if explanation:
        pdf.ln(1)
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(80)
        pdf.multi_cell(0, 5, clean(f"Explanation: {explanation}"),
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0)
    pdf.ln(5)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def _parse_args(argv):
    """Pull an optional `--provider X` flag out; the rest are topics."""
    args = list(argv)
    provider = None
    if "--provider" in args:
        i = args.index("--provider")
        if i + 1 < len(args):
            provider = args[i + 1]
            del args[i:i + 2]
        else:
            del args[i]
    return provider, args


def main():
    provider, topics = _parse_args(sys.argv[1:])
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

    print(f"Generating {len(quizzes)} sample quiz(zes) with provider '{provider}' (model '{model}')...")
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

        safe_name = "".join(c if c.isalnum() else "_" for c in topic).strip("_")[:40]
        path = os.path.join(OUTPUT_DIR, f"{i:02d}_{safe_name}.pdf")
        render_quiz_pdf(quiz, {"topic": topic, "difficulty": difficulty, "model": model}, path)
        generated += 1
        print(f"      OK -> {os.path.relpath(path)}  "
              f"(\"{quiz['title']}\", {len(quiz['questions'])} questions)\n")

        # Be gentle with the free-tier per-minute limit.
        if i < len(quizzes):
            time.sleep(4)

    print("=" * 60)
    print(f"Done. {generated}/{len(quizzes)} quiz PDFs written to {OUTPUT_DIR}")
    if generated:
        print("Open the PDFs to review question quality, options, and explanations.")


TRANSIENT = ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "high demand", "overloaded")


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
            if transient or isinstance(exc, ValueError):
                wait = 15 * attempt
                reason = "model busy/limited" if transient else "bad response, retrying"
                if attempt < attempts:
                    print(f"      {reason}; retrying in {wait}s (attempt {attempt}/{attempts})...")
                    time.sleep(wait)
                    continue
            raise
    raise last


if __name__ == "__main__":
    main()
