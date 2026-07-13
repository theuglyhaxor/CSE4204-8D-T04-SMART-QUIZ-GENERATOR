# Backend API Reference

## Base URL

While developing locally:

- `http://127.0.0.1:8000/api`

The frontend calls `/api/...` and the Vite dev server proxies it here, so the browser never makes a
cross-origin request in development.

## Authentication

Authentication is **JWT** (`djangorestframework-simplejwt`). Register or log in to receive an
`access` token (60 min) and a `refresh` token (1 day, rotating). Send the access token on every
protected request:

```
Authorization: Bearer <access_token>
```

When the access token expires, exchange the refresh token at `POST /auth/token/refresh/`.
`POST /auth/logout/` blacklists a refresh token.

## Roles

Every user belongs to exactly one role group: **`teacher`** or **`student`**. Roles are enforced
server-side on every endpoint. Beyond the role, two ownership rules apply:

- A teacher may only **update or delete quizzes they created** (`Quiz.created_by`).
- A student may only **read their own attempts** (`QuizAttempt.student`).

## What the backend does

This backend is the source of truth for quiz data and scoring. It stores quizzes, questions and student
attempts, generates quizzes with AI (Gemini or Claude) server-side, and renders quizzes to PDF.

### Core responsibilities

- Persist quiz metadata, questions and answer explanations.
- Enforce role-based access and ownership.
- Return student-safe question data (answers stripped) for quiz-taking.
- Calculate scores and store attempt history against the authenticated user.
- Call the AI provider and create generated quizzes and questions.
- Render a quiz to PDF, with or without the answer key.

### Current behavior that has been verified

- `GET /api/quizzes/` returns quiz records with `question_count`.
- `GET /api/quizzes/<id>/student-questions/` returns a student-safe payload.
- `POST /api/quizzes/<id>/submit/` returns score information.
- `POST /api/ai/generate-quiz/` returns `503` until `GEMINI_API_KEY` is configured.

## Authentication and role-based access

Authentication uses **JWT** (`djangorestframework-simplejwt`). Each login or
registration returns a short-lived **access** token and a longer-lived
**refresh** token. The user's role is embedded as a claim in the JWT.

- Access token lifetime: **60 minutes**
- Refresh token lifetime: **1 day** (rotates on refresh; the previous refresh
  token is blacklisted)

### Auth endpoints

- `POST /api/auth/register/` — create a user, assign `teacher`/`student`, return `{access, refresh, user}`.
- `POST /api/auth/login/` — authenticate, return `{access, refresh, user}`.
- `POST /api/auth/token/refresh/` — exchange `{refresh}` for a new `{access}`.
- `POST /api/auth/logout/` — blacklist the supplied `{refresh}` token (requires a valid `Bearer` access header).

### Role behavior

- **Teacher** accounts can create, update, delete, and inspect quizzes, questions, attempts, and AI-generated quizzes.
- **Student** accounts can fetch student-safe questions and submit quiz attempts.
- All protected endpoints require `Authorization: Bearer <access_token>`.

### Example login request

```json
{
  "username": "teacher1",
  "password": "Test@123"
}
```

### Example login response

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": { "id": 1, "username": "teacher1", "role": "teacher" }
}
```

### Using the token

Send the access token on every protected request:

```
Authorization: Bearer <access_token>
```

When the access token expires (HTTP 401), get a new one without re-login:

```json
POST /api/auth/token/refresh/
{ "refresh": "<refresh_token>" }
```

---

## Data model summary

### Quiz

Fields:

- `id`
- `title`
- `description`
- `difficulty`
- `duration_minutes`
- `is_active`
- `created_at`
- `updated_at`
- `question_count` (computed in the serializer)

### Question

Fields:

- `id`
- `quiz`
- `prompt`
- `option_a`
- `option_b`
- `option_c`
- `option_d`
- `correct_option`
- `explanation`
- `order`

### QuizAttempt

Fields:

- `id`
- `quiz`
- `student_name`
- `responses`
- `score`
- `total`
- `created_at`

---

## Endpoints

### 1. List quizzes

- **Method:** `GET`
- **Path:** `/quizzes/`

This endpoint returns all quizzes together with a `question_count` value.

**Example response:**

```json
[
  {
    "id": 1,
    "title": "Biology Basics",
    "description": "Practice quiz for class 10 science",
    "difficulty": "Medium",
    "duration_minutes": 10,
    "is_active": true,
    "created_at": "2026-05-25T07:07:21.146673Z",
    "updated_at": "2026-05-25T07:07:21.146707Z",
    "question_count": 3
  }
]
```

### 2. Create quiz

- **Method:** `POST`
- **Path:** `/quizzes/`

**Request body:**

```json
{
  "title": "Biology Basics",
  "description": "Practice quiz for class 10 science",
  "difficulty": "Medium",
  "duration_minutes": 10,
  "is_active": true
}
```

**Success response:** `201 Created`

### 3. Retrieve one quiz

- **Method:** `GET`
- **Path:** `/quizzes/<id>/`

Returns a single quiz record.

### 4. Update or delete a quiz

- **Method:** `PUT`, `PATCH`, or `DELETE`
- **Path:** `/quizzes/<id>/`

These methods are available through the default Django REST Framework viewset.

### 5. List questions for a quiz

- **Method:** `GET`
- **Path:** `/quizzes/<id>/questions/`

This endpoint returns the full question payload, including the correct answer and explanation.

**Example response:**

```json
[
  {
    "id": 2,
    "quiz": 2,
    "prompt": "What is the capital of France?",
    "option_a": "Rome",
    "option_b": "Paris",
    "option_c": "Berlin",
    "option_d": "Madrid",
    "correct_option": "B",
    "explanation": "Paris is the capital of France.",
    "order": 1
  }
]
```

### 6. Create a question for a quiz

- **Method:** `POST`
- **Path:** `/quizzes/<id>/questions/`

**Request body:**

```json
{
  "prompt": "What is the capital of France?",
  "option_a": "Rome",
  "option_b": "Paris",
  "option_c": "Berlin",
  "option_d": "Madrid",
  "correct_option": "B",
  "explanation": "Paris is the capital of France.",
  "order": 1
}
```

**Success response:** `201 Created`

### 7. Submit quiz answers

- **Method:** `POST`
- **Path:** `/quizzes/<id>/submit/`

This endpoint validates the submitted answers, compares them against the stored answers, calculates the score, and stores an attempt.

**Request body:**

```json
{
  "student_name": "Student Name",
  "answers": [
    {
      "question": 2,
      "selected_option": "B"
    }
  ]
}
```

**Response example:**

```json
{
  "quiz": 2,
  "student_name": "Student Name",
  "score": 1,
  "total": 1,
  "percentage": 100.0,
  "responses": [
    {
      "question": 2,
      "selected_option": "B",
      "correct_option": "B",
      "is_correct": true
    }
  ],
  "attempt_id": 2
}
```

### 8. List quiz attempts

- **Method:** `GET`
- **Path:** `/quizzes/<id>/attempts/`

Returns all stored attempts for a quiz.

### 9. Student-safe questions

- **Method:** `GET`
- **Path:** `/quizzes/<id>/student-questions/`

This endpoint is intended for the student experience. It excludes the correct answer and explanation.

**Example response:**

```json
[
  {
    "id": 1,
    "prompt": "What is 2 + 2?",
    "option_a": "3",
    "option_b": "4",
    "option_c": "5",
    "option_d": "6",
    "order": 1
  }
]
```

### 10. Parse an uploaded document

- **Method:** `POST`
- **Path:** `/documents/parse/`

This endpoint is **teacher-only**. It accepts a multipart file upload and extracts text from PDF, TXT, MD, CSV, or JSON files.

**Multipart form field:**

- `file`

**Example response:**

```json
{
  "filename": "lecture-notes.pdf",
  "text": "Uploaded lecture notes text",
  "page_count": 2,
  "word_count": 5
}
```

### 11. Generate quiz with Gemini

- **Method:** `POST`
- **Path:** `/ai/generate-quiz/`

This endpoint is server-side only. It takes generation instructions, calls Gemini, validates the returned JSON, creates a quiz, and stores the generated questions.

**Request body:**

```json
{
  "title": "Biology Quiz",
  "difficulty": "Medium",
  "question_count": 5,
  "topic": "Cell structure",
  "syllabus": "Mitochondria, nucleus, cell membrane",
  "instruction": "Generate clear multiple-choice questions.",
  "duration_minutes": 8
}
```

**Success response:** `201 Created`

**Failure cases:**

- `400 Bad Request` when input is invalid or Gemini returns invalid JSON.
- `503 Service Unavailable` when `GEMINI_API_KEY` is not configured.
- `502 Bad Gateway` when Gemini returns fewer questions than requested.

---

## Validation and error behavior

### Input validation

The backend validates:

- `question_count` must be an integer greater than zero.
- `duration_minutes` must be an integer.
- `selected_option` must be present for each submitted answer.
- Each answer must reference a valid question in the quiz.

### Current limitations

- Gemini is available but not active until `GEMINI_API_KEY` is configured.
- Production-grade background queueing is not implemented yet.
- CORS is configured for specific origins and must be updated for any new frontend host.

---

## Production hardening checklist

Before production use, consider:

- Replace the default Django secret key.
- Add authentication and role-based permissions.
- Add request throttling and server-side validation.
- Use a dedicated database user instead of `root`.
- Move off the development server to a production WSGI server.
- Add logging and audit trails for quiz creation and submissions.

---

## Backend testing checklist

Use this checklist to confirm the backend is working correctly:

1. MySQL is running and the database exists.
2. `python manage.py migrate` completes without errors.
3. `GET /api/quizzes/` returns a JSON array.
4. `GET /api/quizzes/<id>/student-questions/` returns question text and options only.
5. `POST /api/quizzes/<id>/submit/` returns a score and attempt ID.
6. `POST /api/ai/generate-quiz/` returns `201` only when `GEMINI_API_KEY` is configured.

---

## Frontend integration rules

- Treat the backend as the source of truth.
- Use `GET` endpoints to read data.
- Use `POST` for creating quizzes and submitting attempts.
- Keep teacher and student flows separate in the UI.
- Do not expose the API key to the client.

---

# Endpoints added in the full-stack release

## `GET /api/meta/` — team identity

Public. Backs the footer in the app **and** the footer stamped onto every exported PDF, so the two can
never drift apart. Source of truth: `TEAM` in `backend/smart_quiz_backend/settings.py`.

```json
{
  "course": "CSE4204 — Mobile Computing Lab",
  "team_id": "CSE4204-8D-T04",
  "project": "Smart Quiz Generator",
  "department": "Department of Computer Science and Engineering",
  "university": "Northern University of Business and Technology, Khulna",
  "members": [
    { "name": "MD Rohan", "student_id": "11220320958", "role": "Backend Developer, Full Stack" }
  ]
}
```

## `GET /api/stats/` — dashboard counters

Requires auth. The shape depends on the caller's role.

**Teacher** (scoped to quizzes they own):

```json
{
  "role": "teacher",
  "total_quizzes": 4,
  "active_quizzes": 3,
  "total_questions": 22,
  "total_attempts": 17,
  "average_score": 68.4
}
```

**Student** (scoped to their own activity):

```json
{
  "role": "student",
  "available_quizzes": 3,
  "quizzes_taken": 2,
  "total_attempts": 3,
  "average_score": 71.5,
  "best_score": 90.0
}
```

## `GET /api/auth/me/` — current user

Requires auth. Used by the frontend to confirm a stored token is still valid on boot.

```json
{ "id": 7, "username": "teacher1", "email": "t@example.com", "role": "teacher" }
```

## `GET /api/attempts/me/` — a student's own attempt history

Student only. Returns **only** the caller's attempts — a student can never read another student's
results through this endpoint.

```json
[
  {
    "id": 12, "quiz": 3, "quiz_title": "Photosynthesis",
    "student": 9, "student_name": "student1",
    "score": 4, "total": 5, "percentage": 80.0,
    "responses": [ /* … */ ],
    "created_at": "2026-07-13T09:14:22Z"
  }
]
```

## `GET /api/quizzes/{id}/export-pdf/` — download the quiz as a PDF

Returns `application/pdf` as a file attachment.

| Query | Who | Result |
|---|---|---|
| *(none)* or `?answers=true` | **teacher** | **Answer key**: correct option highlighted, explanations, and an answer-key page |
| `?answers=false` | teacher | **Student handout**: questions and options only |
| *anything* | **student** | Always the **handout** — a student can never obtain the answer key this way |

Rendered by `backend/quiz_api/pdf.py`, the same renderer used by the offline review CLI. Every page
carries the team identity footer.

```bash
curl -H "Authorization: Bearer $ACCESS" \
     http://127.0.0.1:8000/api/quizzes/3/export-pdf/ -o quiz.pdf
```

---

# Behaviour changes worth knowing

| Change | Why |
|---|---|
| A new quiz is a **draft** (`is_active: false`) | Previously it defaulted to active, publishing an empty quiz to students the moment it was created. Publish with `PATCH /quizzes/{id}/ {"is_active": true}`. |
| `GET /quizzes/` **filters by role** | Students only ever see published quizzes. Teachers see all of theirs, drafts included. |
| Quizzes have an **owner** (`created_by`) | A teacher may only update or delete quizzes they created — otherwise **403**. |
| Attempts are bound to the **authenticated user** | `student_name` in the request body is ignored; the server records the logged-in student. A student can no longer submit under someone else's name. |
| Unknown ids return **404**, not 500 | The quiz-scoped views used an unguarded `Quiz.objects.get()`, which surfaced `DoesNotExist` as a 500. |
| `correct_option` is **normalised** | `"a"` is accepted and stored as `"A"`. |
| `order` is **auto-assigned** | Posting to `/quizzes/{id}/questions/` without `order` appends to the end instead of colliding on 1. |
| Registration enforces the **password policy** | Django's `AUTH_PASSWORD_VALIDATORS` now run on the API, so weak passwords are rejected with a 400. |
