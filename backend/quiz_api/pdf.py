"""
Quiz -> PDF rendering.

This is the single renderer used by BOTH callers, so the PDF a teacher downloads
from the app is byte-for-byte the same layout the review CLI produces:

    quiz_api/views.py                      -> QuizExportPDFView   (GET .../export-pdf/)
    ai_integration/generate_sample_quizzes_pdf.py -> offline quality review

It deliberately takes plain dicts rather than Django model instances, so the CLI
can render a freshly generated quiz that was never saved to the database.

Every page carries the team identity footer (see settings.TEAM).
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path

from django.conf import settings
from fpdf import FPDF
from fpdf.enums import Align, XPos, YPos

# --- Palette ------------------------------------------------------------------
INDIGO = (79, 70, 229)
INK = (15, 23, 42)
MUTED = (100, 116, 139)
HAIRLINE = (226, 232, 240)
WASH = (248, 250, 252)
GREEN = (22, 163, 74)
GREEN_WASH = (240, 253, 244)

OPTION_LABELS = ("A", "B", "C", "D")

# --- Fonts --------------------------------------------------------------------
# fpdf2's built-in Helvetica is latin-1 only, which mangles the curly quotes, dashes
# and symbols the models routinely emit. Prefer a real Unicode TTF when the host has
# one; fall back to Helvetica + transliteration so rendering never hard-fails.
_FONT_CANDIDATES = (
    Path("C:/Windows/Fonts/segoeui.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/Library/Fonts/Arial.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
)

_TRANSLITERATE = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "…": "...", " ": " ",
    "•": "-", "→": "->", "°": " deg", "×": "x",
    "≥": ">=", "≤": "<=", "≠": "!=",
}


def _find_font():
    """Return (regular, bold, italic) TTF paths, or None when no Unicode font exists."""
    for regular in _FONT_CANDIDATES:
        if not regular.exists():
            continue
        stem = regular.stem
        bold = regular.with_name(f"{stem}b{regular.suffix}")
        italic = regular.with_name(f"{stem}i{regular.suffix}")
        # DejaVu uses a different naming convention than the Windows fonts.
        if not bold.exists():
            bold = regular.with_name(regular.name.replace("Sans.ttf", "Sans-Bold.ttf"))
        if not italic.exists():
            italic = regular.with_name(regular.name.replace("Sans.ttf", "Sans-Oblique.ttf"))
        return regular, bold if bold.exists() else regular, italic if italic.exists() else regular
    return None


class QuizPDF(FPDF):
    """A4 quiz document with a persistent team-identity footer."""

    def __init__(self, quiz_title: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.quiz_title = quiz_title
        self.set_margins(16, 16, 16)
        self.set_auto_page_break(auto=True, margin=24)  # room for the footer
        self.set_title(quiz_title)
        self.set_author(settings.TEAM["team_id"])
        self.set_creator(settings.TEAM["project"])

        found = _find_font()
        if found:
            regular, bold, italic = found
            self.add_font("Body", "", str(regular))
            self.add_font("Body", "B", str(bold))
            self.add_font("Body", "I", str(italic))
            self.base_font = "Body"
            self.unicode_ok = True
        else:
            self.base_font = "Helvetica"
            self.unicode_ok = False

    # -- text safety -----------------------------------------------------------
    def text_of(self, value) -> str:
        """Normalise text for whichever font we ended up with."""
        text = str(value or "")
        if self.unicode_ok:
            return text
        for bad, good in _TRANSLITERATE.items():
            text = text.replace(bad, good)
        return text.encode("latin-1", "replace").decode("latin-1")

    def font(self, style: str = "", size: int = 11):
        self.set_font(self.base_font, style, size)

    # -- footer ----------------------------------------------------------------
    def footer(self):
        team = settings.TEAM
        self.set_y(-18)

        self.set_draw_color(*HAIRLINE)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)

        usable = self.w - self.l_margin - self.r_margin
        third = usable / 3

        self.font("B", 7)
        self.set_text_color(*INDIGO)
        self.cell(third, 4, self.text_of(f"{team['team_id']}  |  {team['project']}"), align=Align.L)

        self.font("", 7)
        self.set_text_color(*MUTED)
        self.cell(third, 4, self.text_of(team["course"]), align=Align.C)
        self.cell(third, 4, self.text_of(f"Page {self.page_no()} of {{nb}}"), align=Align.R)

        self.ln(4)
        self.font("", 6.5)
        self.set_text_color(*MUTED)
        self.cell(0, 3.5, self.text_of(f"{team['department']}, {team['university']}"), align=Align.C)

        self.set_text_color(*INK)


# --- building blocks ----------------------------------------------------------
def _title_band(pdf: QuizPDF, quiz: dict):
    """Full-bleed indigo header with the quiz title."""
    pdf.set_fill_color(*INDIGO)
    pdf.rect(0, 0, pdf.w, 34, style="F")

    pdf.set_xy(pdf.l_margin, 9)
    pdf.set_text_color(199, 210, 254)
    pdf.font("B", 8)
    pdf.cell(0, 4, pdf.text_of(settings.TEAM["project"].upper()), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(pdf.l_margin)
    pdf.set_text_color(255, 255, 255)
    pdf.font("B", 19)
    pdf.multi_cell(
        pdf.w - pdf.l_margin - pdf.r_margin, 8,
        pdf.text_of(quiz["title"]),
        new_x=XPos.LMARGIN, new_y=YPos.NEXT,
    )

    pdf.set_y(40)
    pdf.set_text_color(*INK)


def _meta_strip(pdf: QuizPDF, meta: dict):
    """Light key/value bar: difficulty, question count, duration, date, model."""
    items = [
        ("Difficulty", meta.get("difficulty", "Medium")),
        ("Questions", str(meta.get("question_count", 0))),
        ("Duration", f"{meta.get('duration_minutes', 0)} min"),
        ("Generated", meta.get("generated_on") or _dt.date.today().isoformat()),
    ]
    if meta.get("model"):
        items.append(("Model", meta["model"]))

    usable = pdf.w - pdf.l_margin - pdf.r_margin
    height = 13
    top = pdf.get_y()

    pdf.set_fill_color(*WASH)
    pdf.set_draw_color(*HAIRLINE)
    pdf.set_line_width(0.3)
    pdf.rect(pdf.l_margin, top, usable, height, style="DF")

    width = usable / len(items)
    for i, (label, value) in enumerate(items):
        x = pdf.l_margin + i * width
        pdf.set_xy(x + 3, top + 2.5)
        pdf.font("", 6.5)
        pdf.set_text_color(*MUTED)
        pdf.cell(width - 6, 3.5, pdf.text_of(label.upper()), new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.set_x(x + 3)
        pdf.font("B", 9)
        pdf.set_text_color(*INK)
        pdf.cell(width - 6, 4.5, pdf.text_of(value))

    pdf.set_y(top + height + 5)
    pdf.set_text_color(*INK)


def _instructions(pdf: QuizPDF, text: str):
    if not text.strip():
        return
    pdf.font("I", 9)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(0, 4.6, pdf.text_of(text.strip()), align=Align.L,
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*INK)
    pdf.ln(4)


def _question_block(pdf: QuizPDF, index: int, question: dict, include_answers: bool):
    usable = pdf.w - pdf.l_margin - pdf.r_margin
    body_w = usable - 10  # indent past the number badge

    # Estimate the block height and page-break first, so a question is never split
    # across pages with its options orphaned.
    prompt_lines = len(pdf.multi_cell(body_w, 5.6, pdf.text_of(question["prompt"]), dry_run=True, output="LINES"))
    needed = prompt_lines * 5.6 + 4 * 7 + 12
    if include_answers and question.get("explanation"):
        needed += 10
    if pdf.get_y() + needed > pdf.h - 26:
        pdf.add_page()

    top = pdf.get_y()

    # Number badge — a filled circle centred on the first line of the prompt.
    # NOTE: fpdf2's circle() takes the CENTRE as (x, y), despite its docstring
    # claiming the upper-left of the bounding box. Verified against 2.8.7.
    badge_r = 3.4
    badge_cx = pdf.l_margin + badge_r
    badge_cy = top + 2.8
    pdf.set_fill_color(*INDIGO)
    pdf.circle(x=badge_cx, y=badge_cy, radius=badge_r, style="F")

    pdf.set_xy(badge_cx - badge_r, badge_cy - 2)
    pdf.font("B", 7.5)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(badge_r * 2, 4, str(index), align=Align.C)

    # Prompt — left-aligned; justification opens ugly whitespace rivers in long prompts.
    pdf.set_xy(pdf.l_margin + 10, top)
    pdf.font("B", 11)
    pdf.set_text_color(*INK)
    pdf.multi_cell(body_w, 5.6, pdf.text_of(question["prompt"]),
                   align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1.5)

    # Options
    for label in OPTION_LABELS:
        option_text = question.get(f"option_{label.lower()}", "")
        correct = include_answers and label == str(question.get("correct_option", "")).upper()

        y = pdf.get_y()
        if correct:
            pdf.set_fill_color(*GREEN_WASH)
            pdf.rect(pdf.l_margin + 10, y - 0.5, body_w, 6.8, style="F")

        # Lettered chip
        pdf.set_xy(pdf.l_margin + 11.5, y)
        pdf.font("B", 9)
        pdf.set_text_color(*(GREEN if correct else MUTED))
        pdf.cell(5, 5.8, pdf.text_of(label))

        pdf.set_xy(pdf.l_margin + 17, y)
        pdf.font("B" if correct else "", 10)
        pdf.set_text_color(*(GREEN if correct else INK))
        suffix = "   (correct)" if correct else ""
        pdf.multi_cell(body_w - 7, 5.8, pdf.text_of(f"{option_text}{suffix}"),
                       align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(0.8)

    pdf.set_text_color(*INK)

    if include_answers:
        explanation = str(question.get("explanation") or "").strip()
        if explanation:
            pdf.ln(1)
            pdf.set_x(pdf.l_margin + 10)
            pdf.font("I", 8.5)
            pdf.set_text_color(*MUTED)
            pdf.multi_cell(body_w, 4.4, pdf.text_of(f"Why: {explanation}"),
                           align=Align.L, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(*INK)

    pdf.ln(5)


def _answer_key(pdf: QuizPDF, questions: list):
    pdf.add_page()
    pdf.font("B", 15)
    pdf.set_text_color(*INK)
    pdf.cell(0, 9, pdf.text_of("Answer Key"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(*INDIGO)
    pdf.set_line_width(0.8)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 18, pdf.get_y())
    pdf.ln(6)

    for i, question in enumerate(questions, start=1):
        correct = str(question.get("correct_option", "")).upper()
        correct_text = question.get(f"option_{correct.lower()}", "")

        y = pdf.get_y()
        pdf.font("B", 10)
        pdf.set_text_color(*MUTED)
        pdf.cell(8, 6, pdf.text_of(f"{i}."))

        pdf.set_fill_color(*GREEN)
        pdf.set_text_color(255, 255, 255)
        pdf.font("B", 9)
        pdf.cell(6, 5.5, pdf.text_of(correct), align=Align.C, fill=True)

        pdf.set_xy(pdf.l_margin + 18, y)
        pdf.font("", 10)
        pdf.set_text_color(*INK)
        pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 18, 5.5,
                       pdf.text_of(correct_text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)


def _credits(pdf: QuizPDF):
    """Closing block naming the team — the 'identity' page of the document."""
    team = settings.TEAM
    usable = pdf.w - pdf.l_margin - pdf.r_margin

    # 3mm top pad + 5mm heading + 5.2mm per member + 6mm strapline + 3mm bottom pad
    box_h = 17 + 5.2 * len(team["members"])

    if pdf.get_y() + box_h + 8 > pdf.h - 26:
        pdf.add_page()
    else:
        pdf.ln(6)

    top = pdf.get_y()
    pdf.set_fill_color(*WASH)
    pdf.set_draw_color(*HAIRLINE)
    pdf.rect(pdf.l_margin, top, usable, box_h, style="DF")

    pdf.set_xy(pdf.l_margin + 4, top + 3)
    pdf.font("B", 9)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 5, pdf.text_of(f"Developed by Team {team['team_id']}"),
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    for member in team["members"]:
        pdf.set_x(pdf.l_margin + 4)
        pdf.font("B", 8.5)
        pdf.set_text_color(*INK)
        pdf.cell(46, 5.2, pdf.text_of(member["name"]))
        pdf.font("", 8.5)
        pdf.set_text_color(*MUTED)
        pdf.cell(28, 5.2, pdf.text_of(member["student_id"]))
        pdf.cell(0, 5.2, pdf.text_of(member["role"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_x(pdf.l_margin + 4)
    pdf.font("I", 7.5)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 6, pdf.text_of(
        f"{team['course']}  |  {team['department']}, {team['university']}"
    ))
    pdf.set_text_color(*INK)


# --- public API ---------------------------------------------------------------
def render_quiz_pdf(quiz: dict, meta: dict | None = None, include_answers: bool = True) -> bytes:
    """
    Render a quiz to PDF bytes.

    quiz: {"title", "description"?, "questions": [{prompt, option_a..d, correct_option, explanation?}]}
    meta: {"difficulty"?, "duration_minutes"?, "model"?, "generated_on"?}
    include_answers: True stamps the correct option, explanations and an answer key.
                     False produces a clean student handout.
    """
    meta = dict(meta or {})
    questions = quiz.get("questions", [])
    meta.setdefault("question_count", len(questions))

    pdf = QuizPDF(quiz["title"])
    pdf.alias_nb_pages()  # resolves the "{nb}" total-pages placeholder in the footer
    pdf.add_page()

    _title_band(pdf, quiz)
    _meta_strip(pdf, meta)
    _instructions(pdf, str(quiz.get("description") or ""))

    for i, question in enumerate(questions, start=1):
        _question_block(pdf, i, question, include_answers)

    if include_answers and questions:
        _answer_key(pdf, questions)

    _credits(pdf)

    return bytes(pdf.output())


def quiz_to_dict(quiz) -> dict:
    """Adapt a Quiz model instance (with its questions) to the renderer's dict shape."""
    return {
        "title": quiz.title,
        "description": quiz.description,
        "questions": [
            {
                "prompt": q.prompt,
                "option_a": q.option_a,
                "option_b": q.option_b,
                "option_c": q.option_c,
                "option_d": q.option_d,
                "correct_option": q.correct_option,
                "explanation": q.explanation,
            }
            for q in quiz.questions.all()
        ],
    }
