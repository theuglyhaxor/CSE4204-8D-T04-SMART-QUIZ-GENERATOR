"""
Smart Quiz Generator — API screenshot generator.

Runs the exact same end-to-end suite as system_check.py and renders a clean,
Postman-style PNG for every step — request on top, response below, with a
green/red/amber PASS/FAIL/SKIP pill. Drop these straight into the report or the
documentation/ folder; no manual Postman clicking required.

Output (one image per step, numbered in run order):
    00_summary.png
    01_connectivity_protected-route-without-a-token.png
    02_auth_register-teacher.png
    ...

USAGE
    1. Start the server (from the backend/ folder):
         python manage.py migrate
         python manage.py runserver
    2. Run this script (from the backend/ folder):
         python capture_screenshots.py
       Optional — different host and/or output folder:
         python capture_screenshots.py http://127.0.0.1:8000  ../documentation/api_screenshots

Requires Pillow:   pip install pillow
(Everything else — the HTTP suite — is reused from system_check.py.)
"""

import json
import os
import re
import sys

# --- Reuse the diagnostic suite so screenshots always match the tests -------- #
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from system_check import DEFAULT_BASE, fmt_status, run_suite  # noqa: E402

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("This script needs Pillow to render images.")
    print("Install it, then re-run:\n    pip install pillow")
    sys.exit(2)


# --------------------------------------------------------------------------- #
# Palette
# --------------------------------------------------------------------------- #
WHITE = (255, 255, 255)
INK = (17, 24, 39)        # near-black text
MUTED = (107, 114, 128)   # grey labels
BLUE = (37, 99, 235)      # method + URL
AMBER = (180, 83, 9)      # hints / skip
GREEN = (22, 163, 74)
RED = (220, 38, 38)
HEADER_BG = (31, 41, 55)  # dark header bar
SEP = (229, 231, 235)     # separator lines
PANEL = (249, 250, 251)   # faint section background

WIDTH = 1120
PAD = 28
LINE_H = 24
MAX_REQ_LINES = 32
MAX_RESP_LINES = 48


# --------------------------------------------------------------------------- #
# Fonts — prefer Consolas/DejaVu mono; fall back to PIL's bundled font.
# --------------------------------------------------------------------------- #
def _load(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except (OSError, IOError):
            continue
    try:
        return ImageFont.load_default(size)   # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


MONO = ["C:/Windows/Fonts/consola.ttf", "DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
MONO_B = ["C:/Windows/Fonts/consolab.ttf", "DejaVuSansMono-Bold.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"]

FONTS = {
    "title": _load(MONO_B, 20),
    "label": _load(MONO_B, 16),
    "mono": _load(MONO, 16),
    "monob": _load(MONO_B, 16),
    "small": _load(MONO, 14),
    "pill": _load(MONO_B, 15),
}


# --------------------------------------------------------------------------- #
# Text helpers
# --------------------------------------------------------------------------- #
def _text_w(font, text):
    try:
        return font.getlength(text)
    except AttributeError:
        return font.getsize(text)[0]


def wrap(text, font, max_w):
    """Word-wrap, hard-splitting any single token longer than the line."""
    out = []
    for raw_line in text.split("\n"):
        if raw_line == "":
            out.append("")
            continue
        words = raw_line.split(" ")
        cur = ""
        for word in words:
            candidate = word if not cur else cur + " " + word
            if _text_w(font, candidate) <= max_w:
                cur = candidate
                continue
            if cur:
                out.append(cur)
                cur = ""
            while _text_w(font, word) > max_w:
                # Binary-ish trim to the widest prefix that fits.
                lo, hi = 1, len(word)
                while lo < hi:
                    mid = (lo + hi + 1) // 2
                    if _text_w(font, word[:mid]) <= max_w:
                        lo = mid
                    else:
                        hi = mid - 1
                out.append(word[:lo])
                word = word[lo:]
            cur = word
        out.append(cur)
    return out or [""]


def body_to_lines(body, neterr, max_lines):
    if neterr:
        return [f"<network error> {neterr}"]
    if body is None or body == "":
        return ["<empty body>"]
    if isinstance(body, (dict, list)):
        text = json.dumps(body, indent=2, ensure_ascii=False)
    else:
        text = str(body)
    lines = text.split("\n")
    if len(lines) > max_lines:
        lines = lines[:max_lines] + [f"… ({len(lines) - max_lines} more lines)"]
    return lines


def status_color(step):
    return {True: GREEN, False: RED, None: AMBER}[step.ok]


def status_word(step):
    return {True: "PASS", False: "FAIL", None: "SKIP"}[step.ok]


# --------------------------------------------------------------------------- #
# Render one step
# --------------------------------------------------------------------------- #
def render_step(step, out_path):
    usable = WIDTH - 2 * PAD
    items = []   # (text, font_key, color, kind)

    def add(text="", font_key="mono", color=INK, kind="text"):
        if kind in ("section", "sep") or text == "":
            items.append((text, font_key, color, kind))
            return
        for line in wrap(text, FONTS[font_key], usable):
            items.append((line, font_key, color, "text"))

    # REQUEST -------------------------------------------------------------- #
    add("REQUEST", "label", MUTED, "section")
    if step.method == "-":
        add("(no request was sent for this step)", "mono", MUTED)
    else:
        add(f"{step.method}  {step.url}", "monob", BLUE)
        for key, val in step.req_headers.items():
            add(f"{key}: {val}", "small", MUTED)
        if step.req_body is not None:
            add("")
            if step.is_multipart:
                add(str(step.req_body), "mono", INK)
            else:
                for line in body_to_lines(step.req_body, None, MAX_REQ_LINES):
                    add(line, "mono", INK)
    add("", kind="sep")

    # RESPONSE ------------------------------------------------------------- #
    add("RESPONSE", "label", MUTED, "section")
    if step.method == "-":
        add("(skipped — see result below)", "mono", MUTED)
    else:
        add(fmt_status(step.status, step.neterr).upper(), "monob", status_color(step))
        for line in body_to_lines(step.resp_body, step.neterr, MAX_RESP_LINES):
            add(line, "mono", INK)
    add("", kind="sep")

    # RESULT --------------------------------------------------------------- #
    add("RESULT", "label", MUTED, "section")
    add(f"Expected: {step.expected}", "mono", MUTED)
    add(step.message, "monob", status_color(step))
    if step.hint and step.ok is not True:
        add(f"Hint: {step.hint}", "mono", AMBER)

    # Measure -------------------------------------------------------------- #
    def item_h(kind):
        return {"section": 34, "sep": 16}.get(kind, LINE_H)

    header_h = 72
    body_h = sum(item_h(k) for _, _, _, k in items)
    total_h = header_h + PAD + body_h + PAD

    img = Image.new("RGB", (WIDTH, total_h), WHITE)
    draw = ImageDraw.Draw(img)

    # Header bar + status pill.
    draw.rectangle([0, 0, WIDTH, header_h], fill=HEADER_BG)
    title = f"{step.index:02d}.  {step.group} — {step.title}"
    draw.text((PAD, 16), title, font=FONTS["title"], fill=WHITE)
    draw.text((PAD, 44), "Smart Quiz Generator API", font=FONTS["small"], fill=(156, 163, 175))

    pill = status_word(step)
    pw = _text_w(FONTS["pill"], pill) + 28
    px1 = WIDTH - PAD - pw
    draw.rounded_rectangle([px1, 22, WIDTH - PAD, 50], radius=14, fill=status_color(step))
    draw.text((px1 + 14, 27), pill, font=FONTS["pill"], fill=WHITE)

    # Body.
    y = header_h + PAD
    for text, font_key, color, kind in items:
        if kind == "sep":
            draw.line([(PAD, y + 7), (WIDTH - PAD, y + 7)], fill=SEP, width=1)
            y += item_h(kind)
            continue
        if kind == "section":
            draw.rectangle([PAD - 8, y - 2, WIDTH - PAD + 8, y + 26], fill=PANEL)
            draw.text((PAD, y + 4), text, font=FONTS[font_key], fill=color)
            y += item_h(kind)
            continue
        if text:
            draw.text((PAD, y), text, font=FONTS[font_key], fill=color)
        y += item_h(kind)

    img.save(out_path)
    return out_path


# --------------------------------------------------------------------------- #
# Render the summary sheet
# --------------------------------------------------------------------------- #
def render_summary(suite, out_path):
    rows = suite.steps
    header_h = 110
    row_h = 30
    total_h = header_h + len(rows) * row_h + PAD * 2
    img = Image.new("RGB", (WIDTH, total_h), WHITE)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, WIDTH, 80], fill=HEADER_BG)
    draw.text((PAD, 16), "Smart Quiz Generator — API Test Summary", font=FONTS["title"], fill=WHITE)
    counts = f"PASS {suite.passed}   FAIL {suite.failed}   SKIP {suite.skipped}   /  {len(rows)} steps"
    draw.text((PAD, 48), counts, font=FONTS["label"], fill=(209, 213, 219))

    y = header_h
    draw.text((PAD, y), "#", font=FONTS["label"], fill=MUTED)
    draw.text((PAD + 50, y), "RESULT", font=FONTS["label"], fill=MUTED)
    draw.text((PAD + 170, y), "STEP", font=FONTS["label"], fill=MUTED)
    y += row_h
    draw.line([(PAD, y - 4), (WIDTH - PAD, y - 4)], fill=SEP, width=1)

    for step in rows:
        color = status_color(step)
        draw.text((PAD, y), f"{step.index:02d}", font=FONTS["mono"], fill=INK)
        draw.text((PAD + 50, y), status_word(step), font=FONTS["monob"], fill=color)
        label = f"{step.group} — {step.title}"
        if _text_w(FONTS["mono"], label) > WIDTH - PAD - (PAD + 170):
            while _text_w(FONTS["mono"], label + "…") > WIDTH - PAD - (PAD + 170) and len(label) > 4:
                label = label[:-1]
            label += "…"
        draw.text((PAD + 170, y), label, font=FONTS["mono"], fill=INK)
        y += row_h

    img.save(out_path)
    return out_path


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "documentation", "api_screenshots")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    print("Smart Quiz Generator — capturing API screenshots")
    print(f"Target : {base}")
    print(f"Output : {out_dir}\n")

    saved = []

    def on_step(step):
        name = f"{step.index:02d}_{_slug(step.group + '-' + step.title)}.png"
        path = os.path.join(out_dir, name)
        render_step(step, path)
        saved.append(path)
        tag = {True: "PASS", False: "FAIL", None: "SKIP"}[step.ok]
        print(f"  [{tag}] saved {name}")

    suite = run_suite(base, progress=on_step)

    summary_path = os.path.join(out_dir, "00_summary.png")
    render_summary(suite, summary_path)
    print(f"\n  saved 00_summary.png")

    print(f"\nDone. {len(saved)} step image(s) + 1 summary written to:\n  {out_dir}")
    print(f"Result: PASS {suite.passed} / FAIL {suite.failed} / SKIP {suite.skipped}")
    if suite.failed:
        print("Note: some steps FAILED — run 'python system_check.py' for the full error detail.")
    sys.exit(1 if suite.failed else 0)


if __name__ == "__main__":
    main()
