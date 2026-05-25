# SMART QUIZ GENERATOR

**SMART QUIZ GENERATOR** is a backend-first Django application for creating, managing, and scoring quizzes. It also includes a Gemini-based quiz generation flow. 

---

## What this backend does

This backend is responsible for the server-side logic of the quiz system.

### Current capabilities

- Create, list, retrieve, update, and delete quizzes.
- Create and retrieve questions for a quiz.
- Expose a student-safe question endpoint that does **not** include correct answers.
- Score quiz submissions and store attempt history.
- Generate quiz questions by calling Gemini through the backend.
- Provide JSON APIs for a frontend, mobile app, or another service.
- Parse uploaded PDF, TXT, MD, CSV, and JSON files through a teacher-only endpoint.

### Current auth and access control

- Token-based authentication is enabled for protected endpoints.
- Teacher and student roles are enforced through Django groups.
- Teacher endpoints are restricted to teacher accounts.
- Student endpoints are restricted to student accounts.
- File upload / PDF parsing is implemented for teacher accounts.
- Production-grade queueing / background jobs are not implemented yet.
- No dedicated frontend inside this repository.

### What this backend does **not** do yet

This section is here to make the current status explicit. The backend **already supports**:

- file upload / PDF parsing
- teacher and student roles
- token-based authentication

The remaining gaps are:

- production-grade background jobs or queueing
- automatic document-to-quiz generation beyond the existing document parsing endpoint
- a bundled frontend inside this repository

---

## Backend architecture

### Technology stack

- Django 4.2.17
- Django REST Framework
- django-cors-headers
- PyMySQL
- MySQL or MariaDB on XAMPP

### Data model summary

- **Quiz**: quiz metadata such as title, difficulty, duration, and active status.
- **Question**: MCQ content, four answer options, correct option, explanation, and order.
- **QuizAttempt**: saved student responses, score, total, and timestamp.

### Database architecture

A dedicated database architecture guide lives in [docs/DATABASE_ARCHITECTURE.md](docs/DATABASE_ARCHITECTURE.md). It documents the tables, relationships, and role/auth schema used by the Django backend.

### API entry point

- Base URL: `http://127.0.0.1:8001/api`

### Important routes

- `GET /api/quizzes/` — list quizzes
- `POST /api/quizzes/` — create a quiz
- `GET /api/quizzes/<id>/` — retrieve a quiz
- `GET /api/quizzes/<id>/questions/` — list questions for a quiz
- `POST /api/quizzes/<id>/questions/` — create a question for a quiz
- `GET /api/quizzes/<id>/student-questions/` — fetch student-safe questions only
- `POST /api/quizzes/<id>/submit/` — submit answers and calculate the score
- `GET /api/quizzes/<id>/attempts/` — list quiz attempts
- `POST /api/documents/parse/` — upload and parse a PDF or text file
- `POST /api/ai/generate-quiz/` — generate a quiz using Gemini

---

## Backend setup on XAMPP

### 1. Start XAMPP services

Start **Apache** and **MySQL** from the XAMPP control panel.

### 2. Create the database

Open a MySQL shell and create the database:

```sql
CREATE DATABASE smart_quiz_generator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Create the Python environment

```powershell
cd D:\SMART-QUIZ-GENERATOR
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

> Always use the virtualenv interpreter for backend commands. The backend should be started with `D:\SMART-QUIZ-GENERATOR\.venv\Scripts\python.exe`, not the system `python` command.

### 4. Configure environment variables

Use PowerShell to set the backend environment before starting Django:

```powershell
$env:DB_NAME = "smart_quiz_generator"
$env:DB_USER = "root"
$env:DB_PASSWORD = ""
$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "3306"
$env:DJANGO_DEBUG = "1"
$env:CORS_ALLOWED_ORIGINS = "http://127.0.0.1:3000,http://localhost:3000"
```

Add Gemini settings when you want AI generation enabled:

```powershell
$env:GEMINI_API_KEY = "your-api-key"
$env:GEMINI_MODEL = "gemini-1.5-flash"
$env:GEMINI_TIMEOUT = "30"
```

> If your XAMPP root user has a password, replace the blank password with your actual password.

### 5. Apply migrations

```powershell
cd backend
python manage.py migrate
```

### 6. Load sample data

```powershell
mysql -u root -p smart_quiz_generator < ..\sample_data.sql
```

If your XAMPP root user has no password, use:

```powershell
mysql -u root smart_quiz_generator < ..\sample_data.sql
```

### 7. Start the backend

```powershell
cd backend
D:\SMART-QUIZ-GENERATOR\.venv\Scripts\python.exe manage.py runserver 8001
```

You should see Django running on `http://127.0.0.1:8001/`.

### 8. Register and log in

Use the auth endpoints to create a teacher or student account and get a token.

```powershell
$register = '{"username":"teacher1","password":"Test@123","role":"teacher"}'
Invoke-WebRequest -Method POST -ContentType "application/json" -Body $register http://127.0.0.1:8001/api/auth/register/ | Select-Object -ExpandProperty Content

$login = '{"username":"teacher1","password":"Test@123"}'
Invoke-WebRequest -Method POST -ContentType "application/json" -Body $login http://127.0.0.1:8001/api/auth/login/ | Select-Object -ExpandProperty Content
```

Use the returned token in later requests:

```powershell
$headers = @{ Authorization = "Token YOUR_TOKEN" }
Invoke-WebRequest -Headers $headers http://127.0.0.1:8001/api/quizzes/ | Select-Object -ExpandProperty Content
```

---

## How to test the backend

### Basic verification

Run these checks after the server starts.

#### 1. Verify the API is alive

```powershell
Invoke-WebRequest http://127.0.0.1:8001/api/quizzes/ | Select-Object -ExpandProperty Content
```

#### 2. Verify the student-safe endpoint

```powershell
Invoke-WebRequest http://127.0.0.1:8001/api/quizzes/1/student-questions/ | Select-Object -ExpandProperty Content
```

#### 3. Verify quiz submission

```powershell
$body = '{"student_name":"Test Student","answers":[{"question":1,"selected_option":"B"}]}'
Invoke-WebRequest -Method POST -ContentType "application/json" -Body $body http://127.0.0.1:8001/api/quizzes/1/submit/ | Select-Object -ExpandProperty Content
```

#### 4. Verify AI generation

```powershell
$body = '{"title":"AI Test Quiz","difficulty":"Medium","question_count":2,"topic":"Science","syllabus":"Cells and planets","instruction":"Generate two clear MCQs.","duration_minutes":5}'
Invoke-WebRequest -Method POST -ContentType "application/json" -Body $body http://127.0.0.1:8001/api/ai/generate-quiz/ | Select-Object -ExpandProperty Content
```

If `GEMINI_API_KEY` is not set, the response will be `503` and the body will contain `GEMINI_API_KEY is not configured.`

#### 5. Verify document parsing

```powershell
$headers = @{ Authorization = "Token YOUR_TOKEN" }
$files = @{ file = Get-Item .\sample.txt }
Invoke-RestMethod -Method POST -Headers $headers -Form $files http://127.0.0.1:8001/api/documents/parse/
```

### What a healthy backend looks like

A healthy backend should show:

- `GET /api/quizzes/` returns JSON quiz objects.
- `GET /api/quizzes/<id>/student-questions/` returns only question text and options.
- `POST /api/quizzes/<id>/submit/` returns a score and attempt details.
- `POST /api/ai/generate-quiz/` returns `201` once Gemini is configured.

---

## How to build the frontend separately

This repository does not contain the UI anymore. Build the frontend as a separate project and make it call the backend APIs.

### Recommended frontend approach

- Use **React + Vite**, **Vue**, or plain HTML/JS if you want a lightweight starter.
- Keep the frontend in its own folder or repository.
- Store the API base URL in one place.
- Use the backend only for data and AI generation.
- Never place `GEMINI_API_KEY` on the client.

### Frontend responsibilities

- Teacher dashboard: create quizzes, add questions, view attempts.
- Student portal: list quizzes, fetch student-safe questions, submit answers.
- Results screen: show scores and attempt history.

### CORS requirements

Add your frontend origin to `CORS_ALLOWED_ORIGINS`, for example:

```powershell
$env:CORS_ALLOWED_ORIGINS = "http://127.0.0.1:3000,http://localhost:3000"
```

### Frontend integration guide

See [docs/FRONTEND_DEVELOPER_GUIDE.md](docs/FRONTEND_DEVELOPER_GUIDE.md) for a detailed frontend contract and example API usage.

---

## Gemini AI integration

The AI flow is server-side only.

### Current AI behavior

1. The frontend sends generation details to `POST /api/ai/generate-quiz/`.
2. The backend validates input and calls Gemini.
3. The backend validates the Gemini response.
4. The backend creates a `Quiz` record and linked `Question` records.
5. The backend returns the created quiz and generated questions.

### Required environment variables

- `GEMINI_API_KEY`
- `GEMINI_MODEL` (optional, defaults to `gemini-1.5-flash`)
- `GEMINI_TIMEOUT` (optional, defaults to `30`)

### AI validation rules

- Exactly four options are required.
- `correct_option` must be `A`, `B`, `C`, or `D`.
- The generated payload must include a non-empty title.
- The response must contain the requested number of questions.

See [docs/AI_INTEGRATION_GUIDE.md](docs/AI_INTEGRATION_GUIDE.md) for a full implementation guide.

---

## Documentation

- [Backend API Reference](docs/BACKEND_API_REFERENCE.md)
- [Frontend Developer Guide](docs/FRONTEND_DEVELOPER_GUIDE.md)
- [Gemini AI Integration Guide](docs/AI_INTEGRATION_GUIDE.md)

---

## Important notes

- The backend currently uses `AllowAny` for API access, so authentication is still missing.
- Use the sample SQL script at the project root to seed a local testing database.
- The current backend is designed for local development and should be hardened before production deployment.
