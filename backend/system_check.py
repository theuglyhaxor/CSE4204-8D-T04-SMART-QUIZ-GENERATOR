"""
Smart Quiz Generator — full-system diagnostic.

Drives the REAL running Django server over HTTP and exercises every feature end
to end. Unlike a plain smoke test, every failure prints THREE things so you can
fix it fast:

    * the exact HTTP status we got vs. what was expected,
    * the server's own response body (its error message), and
    * a "Hint:" line with the most likely cause and the command/fix.

It is stdlib-only (no 'requests' dependency) and safe to re-run: every object is
created with a unique suffix and the quizzes it creates are deleted at the end.

USAGE
    1. Start the server in one terminal (from the backend/ folder):
         python manage.py migrate
         python manage.py runserver          # serves http://127.0.0.1:8000
    2. Run this script in another terminal (from the backend/ folder):
         python system_check.py
       Optional — point at a different host/port:
         python system_check.py http://127.0.0.1:8001

This module also exposes run_suite(), which capture_screenshots.py imports so the
screenshots match exactly what this diagnostic tests.
"""

import json
import sys
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from urllib import error, request

DEFAULT_BASE = "http://127.0.0.1:8000"


# --------------------------------------------------------------------------- #
# Step record — one API call, its request, its response, and the verdict.
# capture_screenshots.py renders one image per Step.
# --------------------------------------------------------------------------- #
@dataclass
class Step:
    index: int
    group: str
    title: str
    method: str
    url: str
    req_headers: dict
    req_body: Any
    is_multipart: bool
    expected: str
    status: Optional[int]
    resp_body: Any
    neterr: Optional[str]
    ok: Optional[bool]          # True = pass, False = fail, None = skipped
    message: str
    hint: str = ""


# --------------------------------------------------------------------------- #
# Small formatting helpers
# --------------------------------------------------------------------------- #
def fmt_status(status, neterr):
    if neterr:
        return "connection error"
    if status is None:
        return "no response"
    return f"HTTP {status}"


def short(body, limit=240):
    """Single-line, length-capped repr of a response body for log lines."""
    if body is None or body == "":
        return "<empty body>"
    text = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit] + " …"


def hint_for(status, neterr):
    """Most likely cause + fix for a given failure, in plain language."""
    if neterr:
        return (f"Server unreachable ({neterr}). Start it: "
                "cd backend && python manage.py runserver")
    if status is None:
        return "No HTTP response — is the server running on this host/port?"
    if status == 500:
        return ("Server error 500 — read the traceback in the runserver console. "
                "Common causes: migrations not applied (run 'python manage.py "
                "migrate') or the database is unreachable / misconfigured in backend/.env.")
    if status == 401:
        return "Unauthorized — the token is missing/expired or the credentials are wrong."
    if status == 403:
        return "Forbidden — this user's role is not allowed to perform this action."
    if status == 404:
        return "Not found — check the URL path and that the referenced id exists."
    if status == 503:
        return ("Service unavailable — for AI generation set GEMINI_API_KEY in "
                "backend/.env (or ANTHROPIC_API_KEY with provider='claude'), then restart the server.")
    if status == 502:
        return ("Bad gateway — the AI model returned fewer questions than requested. "
                "Try a smaller question_count or a simpler topic.")
    if status == 400:
        return "Bad request — the payload failed validation; see the response body above for the field."
    return ""


# --------------------------------------------------------------------------- #
# Low-level HTTP (stdlib only)
# --------------------------------------------------------------------------- #
def _parse(raw):
    if not raw:
        return ""
    try:
        return json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return raw.decode("utf-8", errors="replace")


def _http(method, url, headers, data, timeout=60):
    """Return (status, parsed_body, neterr).  neterr is None on an HTTP reply."""
    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return resp.status, _parse(resp.read()), None
    except error.HTTPError as exc:
        return exc.code, _parse(exc.read()), None
    except error.URLError as exc:
        return None, None, str(exc.reason)
    except Exception as exc:  # noqa: BLE001 — surface anything else as a clear message
        return None, None, str(exc)


# --------------------------------------------------------------------------- #
# Check builders — each returns (ok, message, hint) given (status, body, neterr)
# --------------------------------------------------------------------------- #
def expect_status(code, ok_msg=None):
    def _check(status, body, neterr):
        if status == code:
            return True, ok_msg or f"Got HTTP {code} as expected", ""
        return (False,
                f"Expected HTTP {code}, got {fmt_status(status, neterr)} -> {short(body)}",
                hint_for(status, neterr))
    return _check


def expect_2xx(ok_msg=None):
    def _check(status, body, neterr):
        if status is not None and 200 <= status < 300:
            return True, ok_msg or f"Got {fmt_status(status, neterr)}", ""
        return (False,
                f"Expected 2xx, got {fmt_status(status, neterr)} -> {short(body)}",
                hint_for(status, neterr))
    return _check


# --------------------------------------------------------------------------- #
# Suite — runs every phase, collects Steps, prints a live log.
# --------------------------------------------------------------------------- #
class Suite:
    def __init__(self, base_url, progress=None):
        self.base = base_url.rstrip("/")
        self.api = f"{self.base}/api"
        self.ctx = {}
        self.steps = []
        self.suffix = uuid.uuid4().hex[:8]
        self.progress = progress          # optional callback(step) for live capture

    # -- core call -------------------------------------------------------- #
    def call(self, group, title, method, path, *, token=None, json_body=None,
             multipart=None, expected="2xx", check=None):
        url = path if path.startswith("http") else f"{self.api}{path}"
        headers, disp_headers, data = {}, {}, None
        is_mp = False
        req_disp = None

        if token:
            headers["Authorization"] = f"Bearer {token}"
            disp_headers["Authorization"] = f"Bearer {token[:18]}… ({len(token)} chars)"

        if multipart is not None:
            is_mp = True
            boundary = f"----b{uuid.uuid4().hex}"
            body = bytearray()
            parts = []
            for fname, (filename, content, ctype) in multipart.items():
                body += f"--{boundary}\r\n".encode()
                body += (f'Content-Disposition: form-data; name="{fname}"; '
                         f'filename="{filename}"\r\n').encode()
                body += f"Content-Type: {ctype}\r\n\r\n".encode()
                body += content + b"\r\n"
                parts.append(f"{fname}={filename} ({ctype}, {len(content)} bytes)")
            body += f"--{boundary}--\r\n".encode()
            data = bytes(body)
            headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
            disp_headers["Content-Type"] = "multipart/form-data"
            req_disp = "form-data: " + ", ".join(parts)
        elif json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"
            disp_headers["Content-Type"] = "application/json"
            req_disp = json_body

        status, body, neterr = _http(method, url, headers, data)
        ok, message, hint = (check or expect_2xx())(status, body, neterr)

        step = Step(
            index=len(self.steps) + 1, group=group, title=title, method=method,
            url=url, req_headers=disp_headers, req_body=req_disp, is_multipart=is_mp,
            expected=expected, status=status, resp_body=body, neterr=neterr,
            ok=ok, message=message, hint=hint,
        )
        self.steps.append(step)
        self._log(step)
        if self.progress:
            self.progress(step)
        return status, body, step

    def skip(self, group, title, message, hint=""):
        step = Step(
            index=len(self.steps) + 1, group=group, title=title, method="-", url="-",
            req_headers={}, req_body=None, is_multipart=False, expected="n/a",
            status=None, resp_body=None, neterr=None, ok=None, message=message, hint=hint,
        )
        self.steps.append(step)
        self._log(step)
        if self.progress:
            self.progress(step)
        return step

    def _log(self, step):
        tag = {True: "PASS", False: "FAIL", None: "SKIP"}[step.ok]
        print(f"  [{tag}] {step.index:02d}. {step.group} — {step.title}")
        print(f"         {step.message}")
        if step.ok is False and step.hint:
            print(f"         Hint: {step.hint}")

    # -- summary counters ------------------------------------------------- #
    @property
    def passed(self):
        return sum(1 for s in self.steps if s.ok is True)

    @property
    def failed(self):
        return sum(1 for s in self.steps if s.ok is False)

    @property
    def skipped(self):
        return sum(1 for s in self.steps if s.ok is None)


def _section(title):
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72)


# --------------------------------------------------------------------------- #
# Phases
# --------------------------------------------------------------------------- #
def phase_connectivity(s):
    _section("0. Connectivity & auth enforcement")

    def check(status, body, neterr):
        if neterr or status is None:
            return False, f"Cannot reach {s.base} ({neterr or 'no response'})", hint_for(status, neterr)
        if status == 401:
            return True, f"Server reachable at {s.base}; auth enforced (401 on protected route)", ""
        return True, f"Server reachable at {s.base} (protected route returned HTTP {status})", ""

    s.call("Connectivity", "Protected route without a token", "GET", "/quizzes/",
           expected="401 (auth required)", check=check)


def phase_register(s):
    _section("1. Registration")
    tu, su, pw = f"teacher_{s.suffix}", f"student_{s.suffix}", "SuperSecret123!"
    s.ctx.update(teacher_user=tu, student_user=su, password=pw)

    def check_role(role):
        def _c(status, body, neterr):
            if (status == 201 and isinstance(body, dict) and body.get("access")
                    and body.get("user", {}).get("role") == role):
                return True, f"Registered {role} '{body['user']['username']}' (id={body['user']['id']}); JWT access+refresh issued", ""
            return (False, f"Expected 201 with a {role} JWT pair, got {fmt_status(status, neterr)} -> {short(body)}",
                    hint_for(status, neterr))
        return _c

    _, b, _ = s.call("Auth", "Register teacher", "POST", "/auth/register/",
                     json_body={"username": tu, "email": f"{tu}@example.com", "password": pw, "role": "teacher"},
                     expected="201 + teacher JWT", check=check_role("teacher"))
    if isinstance(b, dict):
        s.ctx["teacher_token"], s.ctx["teacher_refresh"] = b.get("access"), b.get("refresh")

    _, b, _ = s.call("Auth", "Register student", "POST", "/auth/register/",
                     json_body={"username": su, "email": f"{su}@example.com", "password": pw, "role": "student"},
                     expected="201 + student JWT", check=check_role("student"))
    if isinstance(b, dict):
        s.ctx["student_token"], s.ctx["student_refresh"] = b.get("access"), b.get("refresh")

    s.call("Auth", "Duplicate username rejected", "POST", "/auth/register/",
           json_body={"username": tu, "password": pw, "role": "teacher"},
           expected="400 (duplicate)", check=expect_status(400, "Duplicate username correctly rejected (HTTP 400)"))

    return bool(s.ctx.get("teacher_token") and s.ctx.get("student_token"))


def phase_login(s):
    _section("2. Login")

    def check_ok(status, body, neterr):
        if status == 200 and isinstance(body, dict) and body.get("access") and body.get("refresh"):
            return True, f"Login succeeds; role={body['user']['role']}, JWT pair issued", ""
        return False, f"Expected 200 + JWT pair, got {fmt_status(status, neterr)} -> {short(body)}", hint_for(status, neterr)

    s.call("Auth", "Login with correct password", "POST", "/auth/login/",
           json_body={"username": s.ctx["teacher_user"], "password": s.ctx["password"]},
           expected="200 + JWT pair", check=check_ok)

    s.call("Auth", "Login with wrong password", "POST", "/auth/login/",
           json_body={"username": s.ctx["teacher_user"], "password": "wrong-password"},
           expected="401 (rejected)", check=expect_status(401, "Wrong password correctly rejected (HTTP 401)"))


def phase_permissions(s):
    _section("3. Role-based permissions")
    s.call("Permissions", "Student cannot create a quiz", "POST", "/quizzes/",
           token=s.ctx["student_token"], json_body={"title": "Student should not create this"},
           expected="403 (forbidden)", check=expect_status(403, "Student blocked from creating a quiz (HTTP 403)"))

    s.call("Permissions", "Anonymous cannot create a quiz", "POST", "/quizzes/",
           json_body={"title": "anon"},
           expected="401 (unauthorized)", check=expect_status(401, "Anonymous blocked from creating a quiz (HTTP 401)"))


def phase_quiz_crud(s):
    _section("4. Quiz + question CRUD (teacher)")

    def check_created(status, body, neterr):
        if status == 201 and isinstance(body, dict) and body.get("id"):
            return True, f"Created quiz id={body['id']}", ""
        return False, f"Expected 201 with an id, got {fmt_status(status, neterr)} -> {short(body)}", hint_for(status, neterr)

    _, b, _ = s.call("Quizzes", "Create quiz", "POST", "/quizzes/", token=s.ctx["teacher_token"],
                     json_body={"title": f"System Check Quiz {s.suffix}", "description": "Created by system_check.py",
                                "difficulty": "Easy", "duration_minutes": 10},
                     expected="201 + quiz id", check=check_created)
    if not (isinstance(b, dict) and b.get("id")):
        return False
    quiz_id = b["id"]
    s.ctx["quiz_id"] = quiz_id

    questions = [
        ("2 + 2 = ?", "4", "3", "5", "22", "A"),
        ("Capital of France?", "Berlin", "Paris", "Rome", "Madrid", "B"),
        ("H2O is?", "Salt", "Gold", "Water", "Iron", "C"),
    ]
    s.ctx["question_ids"] = []
    for order, (prompt, a, b_, c, d, correct) in enumerate(questions, start=1):
        _, body, _ = s.call("Questions", f"Add question {order} (answer {correct})", "POST",
                            f"/quizzes/{quiz_id}/questions/", token=s.ctx["teacher_token"],
                            json_body={"quiz": quiz_id, "prompt": prompt, "option_a": a, "option_b": b_,
                                       "option_c": c, "option_d": d, "correct_option": correct,
                                       "explanation": f"The answer is {correct}.", "order": order},
                            expected="201 (created)",
                            check=expect_status(201, f"Question {order} created"))
        if isinstance(body, dict) and body.get("id"):
            s.ctx["question_ids"].append(body["id"])

    def check_list(status, body, neterr):
        if status == 200 and isinstance(body, list):
            return True, f"Listed quizzes ({len(body)} total)", ""
        return False, f"Expected 200 + list, got {fmt_status(status, neterr)} -> {short(body)}", hint_for(status, neterr)

    s.call("Quizzes", "List quizzes", "GET", "/quizzes/", token=s.ctx["teacher_token"],
           expected="200 + array", check=check_list)

    def check_count(status, body, neterr):
        if status == 200 and isinstance(body, dict) and body.get("question_count") == 3:
            return True, f"Retrieved quiz; question_count = {body['question_count']} (correct)", ""
        return False, f"Expected 200 + question_count=3, got {fmt_status(status, neterr)} -> {short(body)}", hint_for(status, neterr)

    s.call("Quizzes", "Retrieve quiz (question_count)", "GET", f"/quizzes/{quiz_id}/",
           token=s.ctx["teacher_token"], expected="200, question_count=3", check=check_count)

    new_title = f"Updated Quiz {s.suffix}"

    def check_patch(status, body, neterr):
        if status == 200 and isinstance(body, dict) and body.get("title") == new_title:
            return True, "Quiz title updated via PATCH", ""
        return False, f"Expected 200 + new title, got {fmt_status(status, neterr)} -> {short(body)}", hint_for(status, neterr)

    s.call("Quizzes", "Update quiz title (PATCH)", "PATCH", f"/quizzes/{quiz_id}/",
           token=s.ctx["teacher_token"], json_body={"title": new_title},
           expected="200 + updated title", check=check_patch)
    return True


def phase_student_flow(s):
    _section("5. Student view + submission + scoring")
    quiz_id = s.ctx.get("quiz_id")

    def check_hidden(status, body, neterr):
        if status == 200 and isinstance(body, list) and body:
            if any("correct_option" in q for q in body):
                return False, "SECURITY: student question view leaks 'correct_option'!", \
                    "Remove correct_option from StudentQuestionSerializer fields."
            return True, f"Student sees {len(body)} questions with answers hidden", ""
        return False, f"Expected 200 + list, got {fmt_status(status, neterr)} -> {short(body)}", hint_for(status, neterr)

    s.call("Student", "Student-safe questions (answers hidden)", "GET",
           f"/quizzes/{quiz_id}/student-questions/", token=s.ctx["student_token"],
           expected="200, no correct_option", check=check_hidden)

    qids = s.ctx.get("question_ids", [])
    if len(qids) < 3:
        s.skip("Student", "Submit attempt", "Skipped — not all 3 questions were created.")
        return

    # Q1 right (A), Q2 right (B), Q3 wrong (A instead of C) -> 2/3.
    answers = [
        {"question": qids[0], "selected_option": "A"},
        {"question": qids[1], "selected_option": "B"},
        {"question": qids[2], "selected_option": "A"},
    ]

    def check_score(status, body, neterr):
        if status == 201 and isinstance(body, dict) and body.get("score") == 2 and body.get("total") == 3:
            return True, f"Submission scored correctly: {body['score']}/{body['total']} ({body.get('percentage')}%)", ""
        return False, f"Expected 201 + score 2/3, got {fmt_status(status, neterr)} -> {short(body)}", hint_for(status, neterr)

    s.call("Student", "Submit attempt (expect 2/3)", "POST", f"/quizzes/{quiz_id}/submit/",
           token=s.ctx["student_token"],
           json_body={"student_name": s.ctx["student_user"], "answers": answers},
           expected="201, score 2/3", check=check_score)

    def check_attempts(status, body, neterr):
        if status == 200 and isinstance(body, list) and len(body) >= 1:
            return True, f"Teacher can view {len(body)} attempt(s)", ""
        return False, f"Expected 200 + >=1 attempt, got {fmt_status(status, neterr)} -> {short(body)}", hint_for(status, neterr)

    s.call("Student", "Teacher views attempts", "GET", f"/quizzes/{quiz_id}/attempts/",
           token=s.ctx["teacher_token"], expected="200 + attempts", check=check_attempts)

    s.call("Student", "Student cannot view attempts", "GET", f"/quizzes/{quiz_id}/attempts/",
           token=s.ctx["student_token"], expected="403 (teacher-only)",
           check=expect_status(403, "Student blocked from viewing attempts (HTTP 403)"))


def phase_document_parse(s):
    _section("6. Document parsing (file upload)")
    sample = ("Photosynthesis is the process by which green plants convert sunlight "
              "into chemical energy. Chlorophyll absorbs light.").encode("utf-8")

    def check_parsed(status, body, neterr):
        if status == 200 and isinstance(body, dict) and body.get("word_count", 0) > 0 and "text" in body:
            return True, f"Parsed .txt: {body['word_count']} words, {body.get('page_count')} page(s)", ""
        return False, f"Expected 200 + word_count, got {fmt_status(status, neterr)} -> {short(body)}", hint_for(status, neterr)

    s.call("Documents", "Teacher parses an uploaded .txt", "POST", "/documents/parse/",
           token=s.ctx["teacher_token"], multipart={"file": ("notes.txt", sample, "text/plain")},
           expected="200 + extracted text", check=check_parsed)

    s.call("Documents", "Student cannot parse documents", "POST", "/documents/parse/",
           token=s.ctx["student_token"], multipart={"file": ("notes.txt", sample, "text/plain")},
           expected="403 (teacher-only)", check=expect_status(403, "Student blocked from document parsing (HTTP 403)"))


def phase_ai(s):
    _section("7. AI quiz generation")

    def check_ai(status, body, neterr):
        if status == 201 and isinstance(body, dict) and body.get("questions"):
            return True, f"AI generated a quiz '{body['quiz']['title']}' with {len(body['questions'])} questions", ""
        if status == 503:
            return None, "Skipped — AI provider key not configured (endpoint is wired but cannot make a live call).", \
                "Set GEMINI_API_KEY in backend/.env (or ANTHROPIC_API_KEY + provider='claude') and restart, then re-run."
        return False, f"Expected 201 + questions, got {fmt_status(status, neterr)} -> {short(body)}", hint_for(status, neterr)

    _, b, _ = s.call("AI", "Generate quiz with AI", "POST", "/ai/generate-quiz/",
                     token=s.ctx["teacher_token"],
                     json_body={"title": "AI Biology Quiz", "topic": "Basic biology: cells and photosynthesis",
                                "question_count": 3, "duration_minutes": 5, "difficulty": "Easy"},
                     expected="201 (or 503 if no key)", check=check_ai)
    if isinstance(b, dict) and b.get("quiz"):
        s.ctx["ai_quiz_id"] = b["quiz"]["id"]


def phase_jwt(s):
    _section("8. JWT refresh + logout (token blacklist)")
    student_refresh = s.ctx.get("student_refresh")
    if student_refresh:
        s.call("JWT", "Refresh access token", "POST", "/auth/token/refresh/",
               json_body={"refresh": student_refresh}, expected="200 + new access",
               check=expect_status(200, "Refresh token exchanged for a new access token (HTTP 200)"))
    else:
        s.skip("JWT", "Refresh access token", "Skipped — no student refresh token captured.")

    s.call("JWT", "Logout without a refresh token", "POST", "/auth/logout/",
           token=s.ctx.get("teacher_token"), expected="400 (missing refresh)",
           check=expect_status(400, "Logout without a refresh token correctly rejected (HTTP 400)"))

    teacher_refresh = s.ctx.get("teacher_refresh")
    if not teacher_refresh:
        s.skip("JWT", "Logout + blacklist", "Skipped — no teacher refresh token captured.")
        return

    s.call("JWT", "Logout (blacklist refresh token)", "POST", "/auth/logout/",
           token=s.ctx.get("teacher_token"), json_body={"refresh": teacher_refresh},
           expected="200 (logged out)", check=expect_status(200, "Logout succeeded; refresh token blacklisted (HTTP 200)"))

    s.call("JWT", "Blacklisted refresh is rejected", "POST", "/auth/token/refresh/",
           json_body={"refresh": teacher_refresh}, expected="401 (blacklisted)",
           check=expect_status(401, "Blacklisted refresh token can no longer be used (HTTP 401)"))


def phase_cleanup(s):
    _section("9. Cleanup")
    for key in ("quiz_id", "ai_quiz_id"):
        quiz_id = s.ctx.get(key)
        if not quiz_id:
            continue

        def check_del(status, body, neterr):
            if status in (200, 204):
                return True, f"Deleted quiz id={quiz_id}", ""
            return False, f"Expected 204, got {fmt_status(status, neterr)} -> {short(body)}", hint_for(status, neterr)

        s.call("Cleanup", f"Delete quiz id={quiz_id}", "DELETE", f"/quizzes/{quiz_id}/",
               token=s.ctx["teacher_token"], expected="204 (deleted)", check=check_del)


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def run_suite(base_url=DEFAULT_BASE, progress=None):
    """Run every phase against base_url and return the populated Suite.

    progress, if given, is called with each Step right after it completes — used
    by capture_screenshots.py to render images one by one as the suite runs.
    """
    s = Suite(base_url, progress=progress)
    phase_connectivity(s)

    # If the very first call could not reach the server, stop early with a clear note.
    if s.steps and s.steps[0].ok is False:
        return s

    if not phase_register(s):
        s.skip("Suite", "Remaining phases",
               "Skipped — registration failed, so authenticated tests cannot run.",
               hint="Fix the registration failure above first (often a 500 = DB/migrations).")
        return s

    phase_login(s)
    phase_permissions(s)
    if phase_quiz_crud(s):
        phase_student_flow(s)
    phase_document_parse(s)
    phase_ai(s)
    phase_jwt(s)
    phase_cleanup(s)
    return s


def _print_report(s, elapsed):
    _section("SUMMARY")
    print(f"  PASSED : {s.passed}")
    print(f"  FAILED : {s.failed}")
    print(f"  SKIPPED: {s.skipped}")
    print(f"  TOTAL  : {len(s.steps)} steps in {elapsed:.1f}s")

    if s.failed:
        _section("FAILURES (exact errors)")
        for step in s.steps:
            if step.ok is False:
                print(f"\n  #{step.index:02d} {step.group} — {step.title}")
                print(f"     Request : {step.method} {step.url}")
                print(f"     Expected: {step.expected}")
                print(f"     Got     : {fmt_status(step.status, step.neterr)}")
                print(f"     Server  : {short(step.resp_body, 400)}")
                if step.hint:
                    print(f"     Hint    : {step.hint}")

    if s.skipped:
        print("\n  Skipped steps (not failures):")
        for step in s.steps:
            if step.ok is None:
                print(f"     #{step.index:02d} {step.title} — {step.message}")

    print()
    if s.failed == 0:
        print("  RESULT: All checks passed — the system is working end to end. ✅")
    else:
        print(f"  RESULT: {s.failed} check(s) failed — see the FAILURES section above. ❌")


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE
    print("Smart Quiz Generator — full-system diagnostic")
    print(f"Target: {base}")
    start = time.time()
    suite = run_suite(base)
    _print_report(suite, time.time() - start)
    sys.exit(1 if suite.failed else 0)


if __name__ == "__main__":
    main()
