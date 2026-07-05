"""
End-to-end manual test for the Smart Quiz Generator backend — no frontend needed.

It drives the REAL running Django server over HTTP and exercises every feature:
    - User registration (teacher + student)
    - Login (correct + wrong password)
    - Password change (via Django auth, then verified through the API)
    - Role-based permissions (student blocked from teacher actions)
    - Quiz CRUD (create / list / retrieve / update / delete)
    - Question creation
    - Student question view (answers hidden)
    - Quiz submission + automatic scoring
    - Teacher viewing attempts
    - Document parsing (file upload -> extracted text)
    - AI quiz generation via Gemini (skipped automatically if no API key)

USAGE
    1. Start the server in one terminal:
         python manage.py migrate
         python manage.py runserver
    2. Run this script in another terminal (from the backend/ folder):
         python manual_api_test.py
       Optional: point at a different host
         python manual_api_test.py http://127.0.0.1:8000

Each created object uses a unique suffix, so the script can be run repeatedly
without colliding with existing data. Created quizzes are deleted at the end.
"""

import json
import mimetypes
import os
import sys
import time
import uuid
from urllib import error, request

BASE_URL = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000").rstrip("/")
API = f"{BASE_URL}/api"

# Unique suffix so re-runs never collide on usernames.
SUFFIX = uuid.uuid4().hex[:8]

passed = 0
failed = 0
skipped = 0


# --------------------------------------------------------------------------- #
# Tiny output helpers
# --------------------------------------------------------------------------- #
def section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def ok(msg):
    global passed
    passed += 1
    print(f"  [PASS] {msg}")


def fail(msg):
    global failed
    failed += 1
    print(f"  [FAIL] {msg}")


def skip(msg):
    global skipped
    skipped += 1
    print(f"  [SKIP] {msg}")


def info(msg):
    print(f"         {msg}")


# --------------------------------------------------------------------------- #
# HTTP helper (stdlib only — no 'requests' dependency)
# --------------------------------------------------------------------------- #
def http(method, path, token=None, json_body=None, multipart=None):
    """Return (status_code, parsed_body). parsed_body is dict/list or raw str."""
    url = path if path.startswith("http") else f"{API}{path}"
    headers = {}
    data = None

    if token:
        headers["Authorization"] = f"Bearer {token}"

    if multipart is not None:
        # multipart = {"field": (filename, bytes, content_type)}
        boundary = f"----boundary{uuid.uuid4().hex}"
        body = bytearray()
        for field, (filename, content, ctype) in multipart.items():
            body += f"--{boundary}\r\n".encode()
            body += (
                f'Content-Disposition: form-data; name="{field}"; '
                f'filename="{filename}"\r\n'.encode()
            )
            body += f"Content-Type: {ctype}\r\n\r\n".encode()
            body += content
            body += b"\r\n"
        body += f"--{boundary}--\r\n".encode()
        data = bytes(body)
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    elif json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, data=data, headers=headers, method=method)

    try:
        with request.urlopen(req, timeout=60) as resp:
            return resp.status, _parse(resp.read())
    except error.HTTPError as exc:
        return exc.code, _parse(exc.read())
    except error.URLError as exc:
        return None, str(exc.reason)


def _parse(raw):
    if not raw:
        return ""
    try:
        return json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return raw.decode("utf-8", errors="replace")


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def check_server_up():
    section("0. Server connectivity")
    code, body = http("GET", "/quizzes/")
    if code is None:
        fail(f"Cannot reach {BASE_URL} — is the server running? ({body})")
        print("\nStart it with:  python manage.py runserver")
        sys.exit(1)
    # Unauthenticated request to a protected endpoint should be 401.
    if code == 401:
        ok(f"Server reachable at {BASE_URL} and auth is enforced (401 on protected route)")
    else:
        ok(f"Server reachable at {BASE_URL} (got HTTP {code})")


def test_registration():
    section("1. User registration")
    teacher_user = f"teacher_{SUFFIX}"
    student_user = f"student_{SUFFIX}"
    password = "SuperSecret123!"

    code, body = http("POST", "/auth/register/", json_body={
        "username": teacher_user,
        "email": f"{teacher_user}@example.com",
        "password": password,
        "role": "teacher",
    })
    teacher_token = None
    teacher_refresh = None
    if code == 201 and body.get("user", {}).get("role") == "teacher" and body.get("access"):
        teacher_token = body["access"]
        teacher_refresh = body.get("refresh")
        ok(f"Registered teacher '{teacher_user}' (id={body['user']['id']}, JWT access + refresh issued)")
    else:
        fail(f"Teacher registration failed: HTTP {code} -> {body}")

    code, body = http("POST", "/auth/register/", json_body={
        "username": student_user,
        "email": f"{student_user}@example.com",
        "password": password,
        "role": "student",
    })
    student_token = None
    student_refresh = None
    if code == 201 and body.get("user", {}).get("role") == "student" and body.get("access"):
        student_token = body["access"]
        student_refresh = body.get("refresh")
        ok(f"Registered student '{student_user}' (id={body['user']['id']}, JWT access + refresh issued)")
    else:
        fail(f"Student registration failed: HTTP {code} -> {body}")

    # Duplicate username should be rejected.
    code, body = http("POST", "/auth/register/", json_body={
        "username": teacher_user,
        "password": password,
        "role": "teacher",
    })
    if code == 400:
        ok("Duplicate username correctly rejected (HTTP 400)")
    else:
        fail(f"Duplicate username should be 400, got HTTP {code} -> {body}")

    return {
        "teacher_user": teacher_user,
        "student_user": student_user,
        "password": password,
        "teacher_token": teacher_token,
        "student_token": student_token,
        "teacher_refresh": teacher_refresh,
        "student_refresh": student_refresh,
    }


def test_login(ctx):
    section("2. Login")
    code, body = http("POST", "/auth/login/", json_body={
        "username": ctx["teacher_user"],
        "password": ctx["password"],
    })
    if code == 200 and body.get("access") and body.get("refresh"):
        ok(f"Login succeeds with correct password (role={body['user']['role']}, JWT pair issued)")
    else:
        fail(f"Login with correct password failed: HTTP {code} -> {body}")

    code, body = http("POST", "/auth/login/", json_body={
        "username": ctx["teacher_user"],
        "password": "wrong-password",
    })
    if code == 401:
        ok("Login with wrong password correctly rejected (HTTP 401)")
    else:
        fail(f"Wrong password should be 401, got HTTP {code} -> {body}")


def test_password_change(ctx):
    section("3. Password change")
    info("Note: the API has no password-change endpoint yet, so this changes the")
    info("password through Django's auth layer, then proves it via the login API.")

    new_password = "BrandNewPass456!"
    try:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smart_quiz_backend.settings")
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import django
        django.setup()
        from django.contrib.auth.models import User
        user = User.objects.get(username=ctx["teacher_user"])
        user.set_password(new_password)
        user.save()
        ok("Password updated in the database via Django auth")
    except Exception as exc:  # noqa: BLE001
        fail(f"Could not change password via Django: {exc}")
        return

    # Old password must now fail.
    code, _ = http("POST", "/auth/login/", json_body={
        "username": ctx["teacher_user"],
        "password": ctx["password"],
    })
    if code == 401:
        ok("Old password no longer works (HTTP 401)")
    else:
        fail(f"Old password should now be 401, got HTTP {code}")

    # New password must work.
    code, body = http("POST", "/auth/login/", json_body={
        "username": ctx["teacher_user"],
        "password": new_password,
    })
    if code == 200 and body.get("access"):
        ok("New password works via the login API (HTTP 200)")
        ctx["password"] = new_password
        ctx["teacher_token"] = body["access"]
        ctx["teacher_refresh"] = body.get("refresh")
    else:
        fail(f"New password login failed: HTTP {code} -> {body}")


def test_permissions(ctx):
    section("4. Role-based permissions")
    # Student must NOT be able to create a quiz.
    code, body = http("POST", "/quizzes/", token=ctx["student_token"], json_body={
        "title": "Student should not create this",
    })
    if code == 403:
        ok("Student blocked from creating a quiz (HTTP 403)")
    else:
        fail(f"Student create should be 403, got HTTP {code} -> {body}")

    # No token at all -> 401.
    code, _ = http("POST", "/quizzes/", json_body={"title": "anon"})
    if code == 401:
        ok("Anonymous user blocked from creating a quiz (HTTP 401)")
    else:
        fail(f"Anonymous create should be 401, got HTTP {code}")


def test_quiz_crud(ctx):
    section("5. Quiz + question CRUD (teacher)")
    code, body = http("POST", "/quizzes/", token=ctx["teacher_token"], json_body={
        "title": f"Manual Test Quiz {SUFFIX}",
        "description": "Created by manual_api_test.py",
        "difficulty": "Easy",
        "duration_minutes": 10,
    })
    if code == 201 and body.get("id"):
        quiz_id = body["id"]
        ctx["quiz_id"] = quiz_id
        ok(f"Created quiz id={quiz_id}")
    else:
        fail(f"Quiz creation failed: HTTP {code} -> {body}")
        return

    # Add 3 questions with known correct answers (A, B, C).
    questions = [
        ("2 + 2 = ?", "4", "3", "5", "22", "A"),
        ("Capital of France?", "Berlin", "Paris", "Rome", "Madrid", "B"),
        ("H2O is?", "Salt", "Gold", "Water", "Iron", "C"),
    ]
    created = 0
    for order, (prompt, a, b, c, d, correct) in enumerate(questions, start=1):
        code, body = http(
            "POST", f"/quizzes/{quiz_id}/questions/", token=ctx["teacher_token"],
            json_body={
                "quiz": quiz_id,
                "prompt": prompt,
                "option_a": a, "option_b": b, "option_c": c, "option_d": d,
                "correct_option": correct,
                "explanation": f"The answer is {correct}.",
                "order": order,
            },
        )
        if code == 201:
            created += 1
        else:
            fail(f"Question {order} creation failed: HTTP {code} -> {body}")
    if created == len(questions):
        ok(f"Created {created} questions")
    ctx["correct_answers"] = {1: "A", 2: "B", 3: "C"}  # by order

    # List + retrieve + verify question_count.
    code, body = http("GET", "/quizzes/", token=ctx["teacher_token"])
    if code == 200 and isinstance(body, list):
        ok(f"Listed quizzes ({len(body)} total)")
    else:
        fail(f"Quiz list failed: HTTP {code} -> {body}")

    code, body = http("GET", f"/quizzes/{quiz_id}/", token=ctx["teacher_token"])
    if code == 200 and body.get("question_count") == len(questions):
        ok(f"Retrieved quiz; question_count = {body['question_count']} (correct)")
    else:
        fail(f"Quiz retrieve/question_count wrong: HTTP {code} -> {body}")

    # Update (PATCH).
    code, body = http("PATCH", f"/quizzes/{quiz_id}/", token=ctx["teacher_token"],
                      json_body={"title": f"Updated Quiz {SUFFIX}"})
    if code == 200 and body.get("title") == f"Updated Quiz {SUFFIX}":
        ok("Updated quiz title (PATCH)")
    else:
        fail(f"Quiz update failed: HTTP {code} -> {body}")


def test_student_flow(ctx):
    section("6. Student question view + submission + scoring")
    quiz_id = ctx.get("quiz_id")
    if not quiz_id:
        skip("No quiz available; skipping student flow")
        return

    # Student-facing questions must NOT leak correct_option.
    code, body = http("GET", f"/quizzes/{quiz_id}/student-questions/",
                      token=ctx["student_token"])
    if code == 200 and isinstance(body, list) and body:
        leaks = any("correct_option" in q for q in body)
        if not leaks:
            ok(f"Student sees {len(body)} questions with answers hidden (no correct_option)")
        else:
            fail("Student question view leaks correct_option!")
        question_ids = [q["id"] for q in sorted(body, key=lambda q: q["order"])]
    else:
        fail(f"Student questions fetch failed: HTTP {code} -> {body}")
        return

    # Submit: answer Q1 right (A), Q2 right (B), Q3 wrong (A instead of C) -> 2/3.
    answers = [
        {"question": question_ids[0], "selected_option": "A"},
        {"question": question_ids[1], "selected_option": "B"},
        {"question": question_ids[2], "selected_option": "A"},
    ]
    code, body = http("POST", f"/quizzes/{quiz_id}/submit/", token=ctx["student_token"],
                      json_body={"student_name": ctx["student_user"], "answers": answers})
    if code == 201 and body.get("score") == 2 and body.get("total") == 3:
        ok(f"Submission scored correctly: {body['score']}/{body['total']} "
           f"({body.get('percentage')}%)")
    else:
        fail(f"Submission scoring wrong (expected 2/3): HTTP {code} -> {body}")

    # Teacher views attempts.
    code, body = http("GET", f"/quizzes/{quiz_id}/attempts/", token=ctx["teacher_token"])
    if code == 200 and isinstance(body, list) and len(body) >= 1:
        ok(f"Teacher can view {len(body)} attempt(s)")
    else:
        fail(f"Attempts list failed: HTTP {code} -> {body}")

    # Student must NOT be able to view attempts (teacher-only).
    code, _ = http("GET", f"/quizzes/{quiz_id}/attempts/", token=ctx["student_token"])
    if code == 403:
        ok("Student blocked from viewing attempts (HTTP 403)")
    else:
        fail(f"Student attempts view should be 403, got HTTP {code}")


def test_document_parse(ctx):
    section("7. Document parsing (file upload)")
    sample = (
        "Photosynthesis is the process by which green plants convert "
        "sunlight into chemical energy. Chlorophyll absorbs light."
    ).encode("utf-8")
    code, body = http(
        "POST", "/documents/parse/", token=ctx["teacher_token"],
        multipart={"file": ("notes.txt", sample, "text/plain")},
    )
    if code == 200 and body.get("word_count", 0) > 0 and "text" in body:
        ok(f"Parsed uploaded .txt: {body['word_count']} words, "
           f"{body.get('page_count')} page(s)")
    else:
        fail(f"Document parse failed: HTTP {code} -> {body}")

    # Student must not be allowed to parse documents (teacher-only).
    code, _ = http("POST", "/documents/parse/", token=ctx["student_token"],
                   multipart={"file": ("notes.txt", sample, "text/plain")})
    if code == 403:
        ok("Student blocked from document parsing (HTTP 403)")
    else:
        fail(f"Student parse should be 403, got HTTP {code}")


def test_ai_generation(ctx):
    section("8. AI quiz generation (Gemini)")
    code, body = http("POST", "/ai/generate-quiz/", token=ctx["teacher_token"], json_body={
        "title": "AI Biology Quiz",
        "topic": "Basic biology: cells and photosynthesis",
        "question_count": 3,
        "duration_minutes": 5,
        "difficulty": "Easy",
    })
    if code == 201 and body.get("questions"):
        ok(f"Gemini generated a quiz with {len(body['questions'])} questions")
        info(f"Quiz title: {body['quiz']['title']}")
        ctx["ai_quiz_id"] = body["quiz"]["id"]
    elif code == 503 and "GEMINI_API_KEY" in str(body):
        skip("No GEMINI_API_KEY configured — AI generation endpoint is wired but "
             "cannot make a live call.")
        info("To enable: put GEMINI_API_KEY=... in backend/.env and re-run.")
    else:
        fail(f"AI generation failed: HTTP {code} -> {body}")


def test_jwt_refresh_and_logout(ctx):
    section("9. JWT refresh + logout (token blacklist)")

    # Refresh: exchange a valid refresh token for a new access token.
    refresh = ctx.get("student_refresh")
    if refresh:
        code, body = http("POST", "/auth/token/refresh/", json_body={"refresh": refresh})
        if code == 200 and body.get("access"):
            ok("Refresh token exchanged for a new access token (HTTP 200)")
        else:
            fail(f"Token refresh failed: HTTP {code} -> {body}")
    else:
        skip("No student refresh token captured; skipping refresh check")

    # Logout with no refresh token in the body -> 400.
    code, _ = http("POST", "/auth/logout/", token=ctx.get("teacher_token"))
    if code == 400:
        ok("Logout without a refresh token correctly rejected (HTTP 400)")
    else:
        fail(f"Logout without refresh should be 400, got HTTP {code}")

    # Logout: blacklist the teacher's refresh token.
    teacher_refresh = ctx.get("teacher_refresh")
    if not teacher_refresh:
        skip("No teacher refresh token captured; skipping logout check")
        return

    code, body = http("POST", "/auth/logout/", token=ctx.get("teacher_token"),
                      json_body={"refresh": teacher_refresh})
    if code == 200:
        ok("Logout succeeded and refresh token blacklisted (HTTP 200)")
    else:
        fail(f"Logout failed: HTTP {code} -> {body}")

    # The blacklisted refresh token must no longer work.
    code, _ = http("POST", "/auth/token/refresh/", json_body={"refresh": teacher_refresh})
    if code == 401:
        ok("Blacklisted refresh token can no longer be used (HTTP 401)")
    else:
        fail(f"Blacklisted refresh should be 401, got HTTP {code}")


def cleanup(ctx):
    section("10. Cleanup")
    for key in ("quiz_id", "ai_quiz_id"):
        quiz_id = ctx.get(key)
        if not quiz_id:
            continue
        code, _ = http("DELETE", f"/quizzes/{quiz_id}/", token=ctx["teacher_token"])
        if code in (204, 200):
            ok(f"Deleted quiz id={quiz_id}")
        else:
            info(f"Could not delete quiz id={quiz_id} (HTTP {code}) — clean it up manually if needed")
    info(f"Test users 'teacher_{SUFFIX}' / 'student_{SUFFIX}' were left in the database.")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    print("Smart Quiz Generator — full backend smoke test")
    print(f"Target: {BASE_URL}")
    start = time.time()

    check_server_up()
    ctx = test_registration()
    if not ctx.get("teacher_token") or not ctx.get("student_token"):
        print("\nRegistration failed — cannot continue the rest of the suite.")
        _summary(start)
        sys.exit(1)

    test_login(ctx)
    test_password_change(ctx)
    test_permissions(ctx)
    test_quiz_crud(ctx)
    test_student_flow(ctx)
    test_document_parse(ctx)
    test_ai_generation(ctx)
    test_jwt_refresh_and_logout(ctx)
    cleanup(ctx)
    _summary(start)
    sys.exit(1 if failed else 0)


def _summary(start):
    section("SUMMARY")
    print(f"  PASSED : {passed}")
    print(f"  FAILED : {failed}")
    print(f"  SKIPPED: {skipped}")
    print(f"  Time   : {time.time() - start:.1f}s")
    if failed == 0:
        print("\n  All checks passed. Every feature is working. ")
    else:
        print(f"\n  {failed} check(s) failed — see [FAIL] lines above.")


if __name__ == "__main__":
    main()
