# Backend API Reference

## Base URL

Use the following base URL while developing locally:

- `http://127.0.0.1:8001/api`

## What the backend does

This backend is the source of truth for quiz data and scoring. It stores quizzes, questions, and student attempts, and it can generate quizzes using Gemini through the server side.

> Use the `.venv` interpreter for all backend commands. The backend must be run with `D:/SMART-QUIZ-GENERATOR/.venv/Scripts/python.exe`, not the system `python` executable.

### Core responsibilities

- Persist quiz metadata.
- Persist question data and answer explanations.
- Return student-safe question data for public quiz-taking.
- Calculate marks and store attempt history.
- Call Gemini and create generated quizzes and questions.

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
