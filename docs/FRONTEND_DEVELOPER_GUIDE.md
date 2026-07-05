# Frontend Developer Guide

## Goal

Build a **separate** frontend application that consumes the Django backend and supports:

- viewing available quizzes
- creating and editing quizzes
- taking quizzes
- reviewing submissions
- optionally triggering AI-generated quiz creation

> The current repository no longer includes a bundled frontend. This guide describes how to build the UI as an external app or separate folder.

---

## Local development setup

### Local services

- Backend API: `http://127.0.0.1:8001/api`
- Frontend dev server: choose your own port, for example `http://127.0.0.1:3000`

### Environment assumptions

- XAMPP Apache and MySQL are running
- Django backend is running on port `8001`
- The frontend is hosted on a separate origin during local development

### CORS configuration

Add your frontend origin to the backend environment:

```powershell
$env:CORS_ALLOWED_ORIGINS = "http://127.0.0.1:3000,http://localhost:3000"
```

Restart the backend after changing this value.

### Authentication flow

All protected backend endpoints now require a token.

1. Register a teacher or student account with `POST /api/auth/register/`.
2. Log in with `POST /api/auth/login/` to receive a token.
3. Send `Authorization: Token <token>` on all protected requests.

Use the token header in every request to `/api/quizzes/`, `/api/questions/`, `/api/documents/parse/`, `/api/ai/generate-quiz/`, and `/api/quizzes/<id>/submit/`.

### File upload flow

Teachers can upload a PDF or text file with `POST /api/documents/parse/`.

- Send the file as a multipart form field named `file`.
- Include `Authorization: Token <token>`.
- The backend returns extracted text, filename, page count, and word count.

---

## Recommended frontend stack

You can use any modern UI stack. The simplest options are:

- **React + Vite** for a full SPA
- **Vue + Vite** for a lightweight SPA
- **Plain HTML/CSS/JS** if you want a minimal frontend

### Recommended project structure

- `src/api/client.js` — a shared API helper
- `src/pages/teacher/` — quiz management screens
- `src/pages/student/` — quiz-taking screens
- `src/pages/results/` — attempt history and score display

---

## API contract summary

### Quiz listing

Use `GET /api/quizzes/` to load the list of quizzes.

### Quiz detail

Use `GET /api/quizzes/<id>/` to fetch metadata for one quiz.

### Questions

- Use `GET /api/quizzes/<id>/questions/` when you need the full question payload including `correct_option` and `explanation`.
- Use `GET /api/quizzes/<id>/student-questions/` when the student UI must hide answer data.

### Quiz submission

Use `POST /api/quizzes/<id>/submit/` to submit answers.

### AI generation

Use `POST /api/ai/generate-quiz/` to ask the backend to generate a quiz with Gemini.

### Teacher actions

Use:

- `POST /api/quizzes/`
- `POST /api/quizzes/<id>/questions/`
- `POST /api/documents/parse/`
- `GET /api/quizzes/<id>/attempts/`

---

## Recommended frontend flow

### 1. Teacher creates a quiz

1. Call `POST /api/quizzes/`
2. Store the returned `id`
3. Call `POST /api/quizzes/<id>/questions/` for each question

### 2. Student takes a quiz

1. Call `GET /api/quizzes/`
2. Select a quiz
3. Call `GET /api/quizzes/<id>/student-questions/`
4. Render options as radio buttons or cards
5. Call `POST /api/quizzes/<id>/submit/`

### 3. Teacher reviews results

1. Call `GET /api/quizzes/<id>/attempts/`
2. Display scores, attempt count, and stored answer data

### 4. AI-assisted quiz generation

1. Collect topic, difficulty, question count, and instruction.
2. Call `POST /api/ai/generate-quiz/`
3. Show the generated quiz before saving or publishing it

---

## Expected payload formats

### Quiz object

```json
{
  "id": 1,
  "title": "Biology Basics",
  "description": "Practice quiz",
  "difficulty": "Medium",
  "duration_minutes": 10,
  "is_active": true,
  "created_at": "2026-05-25T07:07:21.146673Z",
  "updated_at": "2026-05-25T07:07:21.146707Z",
  "question_count": 3
}
```

### Full question object

```json
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
```

### Student-safe question object

```json
{
  "id": 1,
  "prompt": "What is 2 + 2?",
  "option_a": "3",
  "option_b": "4",
  "option_c": "5",
  "option_d": "6",
  "order": 1
}
```

### Submission payload

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

### Submission response

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

---

## Sample API client

Create one shared helper so all screens use the same base URL.

```js
const API_BASE_URL = "http://127.0.0.1:8001/api";

export async function fetchJson(path, options = {}) {
  const token = localStorage.getItem("quiz_token");

  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Token ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }

  return response.json();
}
```

---

## Frontend recommendations

### Data handling

- Cache quiz lists and question sets when needed.
- Show loading and error states clearly.
- Keep teacher and student flows separate to avoid exposing answer data.

### Security and privacy

- Do not render `correct_option` or `explanation` to student users unless you intentionally want post-submission review mode.
- Do not store the Gemini API key on the client.
- Perform validation on both the client and server.

### Error handling

Handle these cases in the UI:

- `400 Bad Request`
- `404 Not Found`
- `500 Internal Server Error`
- `503 Service Unavailable` when Gemini is not configured

---

## Suggested implementation checklist

1. Create a single API helper.
2. Build a quiz list screen.
3. Add a teacher quiz creation flow.
4. Add a question builder flow.
5. Add a student quiz-taking flow.
6. Add a score/results view.
7. Add AI generation form and response handling.
8. Update `CORS_ALLOWED_ORIGINS` for your frontend host.

---

## Important backend notes for the frontend team

- Teacher and student permissions are now enforced.
- All protected endpoints require a token from `/api/auth/login/`.
- Gemini generation requires `GEMINI_API_KEY` on the backend.
- Production-grade queueing is still future work.

The frontend must always send `Authorization: Token <token>` for protected requests.
