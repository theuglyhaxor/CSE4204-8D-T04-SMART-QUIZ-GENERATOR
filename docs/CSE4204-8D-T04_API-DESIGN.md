# 5. API DESIGN DOCUMENT
## CSE4204-8D-T04 Smart Quiz Generator

**Description:** This document lists every planned/implemented REST endpoint with its purpose, input data, and expected output. Endpoints are grouped by function. All routes are defined in [`backend/quiz_api/urls.py`](../backend/quiz_api/urls.py) and implemented in [`backend/quiz_api/views.py`](../backend/quiz_api/views.py).

### Conventions
- **Base URL (dev):** `http://127.0.0.1:8001/api/`
- **Format:** JSON request/response (file upload uses `multipart/form-data`).
- **Auth header:** `Authorization: Token <token>` for all protected endpoints.
- **Roles:** `teacher` and `student`, assigned at registration and enforced by DRF permission classes (`IsTeacherUser`, `IsStudentUser`, `IsTeacherOrStudentUser`).
- **Status tags:** ✅ implemented · 🟡 planned (in SRS, not yet coded).

---

## 5.1 Authentication APIs

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/auth/register/` | Public | Register a new user and issue a token ✅ |
| POST | `/auth/login/` | Public | Authenticate and return a token ✅ |
| POST | `/auth/logout/` | Token | Invalidate the current token 🟡 (SRS FR-06) |

### POST `/auth/register/`
- **Purpose:** Create a user account, assign a role group, and return an auth token.
- **Input:** `{ "username": str, "password": str, "role": "teacher"|"student", "email": str? }`
- **Output (201):** `{ "token": str, "user": { "id": int, "username": str, "role": str } }`
- **Errors:** `400` if username already exists or role invalid.

### POST `/auth/login/`
- **Purpose:** Verify credentials and return the user's token.
- **Input:** `{ "username": str, "password": str }`
- **Output (200):** `{ "token": str, "user": { "id": int, "username": str, "role": str } }`
- **Errors:** `401` invalid username/password.

### POST `/auth/logout/` 🟡
- **Purpose:** Delete the caller's token so it can no longer be used.
- **Input:** none (token in header).
- **Output (200):** `{ "detail": "Logged out." }`

---

## 5.2 Quiz APIs

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/quizzes/` | teacher/student | List quizzes ✅ |
| POST | `/quizzes/` | teacher | Create a quiz ✅ |
| GET | `/quizzes/{id}/` | teacher/student | Retrieve a quiz ✅ |
| PUT/PATCH | `/quizzes/{id}/` | teacher | Update a quiz ✅ |
| DELETE | `/quizzes/{id}/` | teacher | Delete a quiz (cascades questions/attempts) ✅ |

### GET `/quizzes/`
- **Purpose:** List all quizzes with a computed `question_count`.
- **Input:** none.
- **Output (200):** array of `{ id, title, description, difficulty, duration_minutes, is_active, created_at, updated_at, question_count }`.

### POST `/quizzes/`
- **Purpose:** Create a quiz (teacher only).
- **Input:** `{ "title": str, "description": str?, "difficulty": str?, "duration_minutes": int?, "is_active": bool? }`
- **Output (201):** the created quiz object.
- **Errors:** `400` validation; `403` if not a teacher.

### GET `/quizzes/{id}/`
- **Purpose:** Retrieve one quiz's metadata.
- **Output (200):** quiz object · **Errors:** `404` not found.

### PUT/PATCH `/quizzes/{id}/`
- **Purpose:** Update quiz fields, including `is_active` to control student access (SRS FR-12).
- **Input:** any quiz fields (PATCH = partial). · **Output (200):** updated quiz.

### DELETE `/quizzes/{id}/`
- **Purpose:** Remove a quiz and all linked questions/attempts.
- **Output (204):** empty.

---

## 5.3 Question APIs (Teacher)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/quizzes/{quiz_id}/questions/` | teacher | List questions for a quiz ✅ |
| POST | `/quizzes/{quiz_id}/questions/` | teacher | Add a question to a quiz ✅ |
| GET | `/questions/?quiz={id}` | teacher | List/filter questions ✅ |
| POST | `/questions/` | teacher | Create a question ✅ |
| GET | `/questions/{id}/` | teacher | Retrieve a question ✅ |
| PUT/PATCH | `/questions/{id}/` | teacher | Update a question ✅ |
| DELETE | `/questions/{id}/` | teacher | Delete a question ✅ |

### POST `/quizzes/{quiz_id}/questions/`
- **Purpose:** Add an MCQ to the given quiz.
- **Input:** `{ "prompt": str, "option_a": str, "option_b": str, "option_c": str, "option_d": str, "correct_option": "A"|"B"|"C"|"D", "explanation": str?, "order": int? }`
- **Output (201):** the created question (includes `correct_option`).
- **Errors:** `400` invalid `correct_option` / missing fields; `403` non-teacher.

### GET `/questions/?quiz={id}`
- **Purpose:** List all questions, optionally filtered by `quiz` query param.
- **Output (200):** array of full question objects (with answers — teacher only).

---

## 5.4 Student Quiz-Taking APIs

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/quizzes/{quiz_id}/student-questions/` | teacher/student | Get questions **without** answers ✅ |
| POST | `/quizzes/{quiz_id}/submit/` | student | Submit answers and get score ✅ |

### GET `/quizzes/{quiz_id}/student-questions/`
- **Purpose:** Return answer-free questions so students cannot see `correct_option`.
- **Output (200):** array of `{ id, prompt, option_a..option_d, order }` (no `correct_option`, no `explanation`).

### POST `/quizzes/{quiz_id}/submit/`
- **Purpose:** Score a student's answers server-side and persist the attempt.
- **Input:** `{ "student_name": str?, "answers": [ { "question": int, "selected_option": "A".."D" }, ... ] }`
- **Output (201):** `{ "quiz": int, "student_name": str, "score": int, "total": int, "percentage": float, "responses": [...], "attempt_id": int }`
- **Errors:** `400` empty/invalid answers list or a question id not in the quiz.

---

## 5.5 Document & AI APIs

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/documents/parse/` | teacher | Upload & extract text from a document ✅ |
| POST | `/ai/generate-quiz/` | teacher | Generate a quiz via Gemini ✅ |

### POST `/documents/parse/`
- **Purpose:** Extract readable text from an uploaded file (PDF/TXT/MD/CSV/JSON).
- **Input:** `multipart/form-data` with a `file` field.
- **Output (200):** `{ "filename": str, "text": str, "page_count": int, "word_count": int }`
- **Errors:** `400` missing file / unsupported type / empty document.

### POST `/ai/generate-quiz/`
- **Purpose:** Generate a complete quiz with questions using Google Gemini, then persist it. See [AI Integration Workflow](CSE4204-8D-T04_AI-WORKFLOW.md).
- **Input:** `{ "title": str?, "topic": str, "syllabus": str?, "difficulty": str?, "question_count": int (>=1), "duration_minutes": int?, "instruction": str? }`
- **Output (201):** `{ "quiz": {quiz object}, "questions": [ {full question objects} ] }`
- **Errors:** `400` bad params / invalid AI payload · `502` fewer questions than requested · `503` `GEMINI_API_KEY` not configured or API request failed.

---

## 5.6 Attempts & Scoring APIs

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/quizzes/{quiz_id}/attempts/` | teacher | List all attempts for a quiz ✅ |

### GET `/quizzes/{quiz_id}/attempts/`
- **Purpose:** Let a teacher review every student submission for a quiz (SRS FR-14, FR-34).
- **Output (200):** array of `{ id, quiz, student_name, responses, score, total, created_at }`.

---

## 5.7 Cross-cutting design notes

- **HTTP semantics:** `GET` read, `POST` create, `PUT/PATCH` update, `DELETE` remove — all return standard codes (`200/201/204/400/401/403/404/502/503`).
- **Server-side scoring:** correct answers never leave the server during quiz-taking, preventing client tampering.
- **Validation:** AI output is structurally validated (exactly 4 options, `correct_option ∈ {A,B,C,D}`, non-empty title) before persistence.
- **Planned (per SRS):** pagination on list endpoints (NFR-04), rate limiting (NFR-10), token expiry (NFR-06), and `/auth/logout/` (FR-06).

---

**Repository:** https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR

**Related Files (GitHub):**
- Full request/response examples: [BACKEND_API_REFERENCE.md](https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/docs/BACKEND_API_REFERENCE.md)
- [AI Integration Workflow](https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/docs/CSE4204-8D-T04_AI-WORKFLOW.md)
- [Activity Diagrams](https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/diagrams/CSE4204-8D-T04_ACTIVITY-DIAGRAM.md)
