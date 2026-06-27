![Northern University of Business and Technology, Khulna](image.png)

# Backend Progress Report
### Smart Quiz Generator — An Intelligent, Role-Based Quiz Management System with AI-Assisted Question Generation

| Field | Detail |
|-------|--------|
| **Project Title** | Smart Quiz Generator |
| **Course** | CSE4204 — Mobile Computing Lab |
| **Report Type** | Backend Progress Report — Authentication, Database & Core APIs |
| **Team** | Team 04 &middot; Section 8D &middot; Batch 8D |
| **Department** | Computer Science & Engineering (CSE) |
| **Submitted To** | **MD Riaz Mahmud**, Assistant Professor, CSE |
| **Institution** | Northern University of Business and Technology, Khulna |
| **Date of Submission** | 27 June 2026 |

---

## Agenda

> This single document combines everything required for the backend progress
> review. The sections below follow the order in which the work was carried out —
> from project definition and database design through API implementation,
> authentication, testing evidence, and current status. Each section links to the
> source file or diagram in the repository for deeper detail.

| # | Section | Focus |
|---|---------|-------|
| 1 | Project Title | What the system is and which AI providers it supports |
| 2 | Team Information | Members, IDs, roles, and contact details |
| 3 | Backend Technology Stack | Languages, frameworks, database, and tooling |
| 4 | Database Design Summary | Tables, relationships, and multi-layer validation |
| 5 | Implemented APIs | Auth, quizzes, questions, attempts, documents & AI |
| 6 | Authentication Workflow | JWT lifecycle and role-based access control |
| 7 | Current Development Progress | Completed work and planned next steps |
| 8 | Screenshots of API Testing | 28-step end-to-end test evidence |
| 9 | GitHub Repository | Repository, branch, and contribution workflow |
| &mdash; | Appendix | How to run and test the backend locally |

---

## 1. Project Title

**Smart Quiz Generator** — an intelligent, role-based quiz management system that
lets teachers create quizzes (manually or with AI from uploaded documents) and
lets students take quizzes with automatic, real-time scoring. AI question
generation supports two interchangeable providers: **Google Gemini** (default)
and **Anthropic Claude**.

---

## 2. Team Information

| No. | Name | Student ID | Role / Responsibility | Email |
|-----|------|-----------|-----------------------|-------|
| 1 | MD Rohan | 11220320958 | Backend Developer, Full-Stack | therohansec@gmail.com |
| 2 | Sharmin Nahar Tumpa | 11220320962 | AI Integration | tumpa540264@gmail.com |
| 3 | Pial Tarofdar | 11220320965 | Frontend Developer | pialtarofdar55@gmail.com |
| 4 | Sanjana Athoy | 11220320953 | Overall Technical Help | sanjanaathoy55@gmail.com |

---

## 3. Backend Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.9+ |
| Framework | Django 4.2 |
| API layer | Django REST Framework (DRF) |
| Authentication | JWT — `djangorestframework-simplejwt` (access + refresh tokens, blacklist) |
| Password security | Django PBKDF2-SHA256 hashing |
| Database | MySQL 5.7+ / MariaDB 10.3+ (InnoDB, utf8mb4) |
| DB driver | PyMySQL |
| CORS | django-cors-headers |
| Document parsing | pypdf + stdlib (txt/md/csv/json) |
| AI providers | Google Gemini (REST) + Anthropic Claude (`anthropic` SDK) |
| API testing | Postman collection + `manual_api_test.py` smoke test |

Configuration is environment-driven (`.env`) — secret key, database credentials,
allowed hosts, CORS origins, and AI keys are all read from the environment in
[`backend/smart_quiz_backend/settings.py`](../backend/smart_quiz_backend/settings.py).

---

## 4. Database Design Summary

**DBMS:** MySQL (InnoDB, `utf8mb4`). The schema is created and versioned by Django
migrations; a human-readable reference DDL and seed script live in the
[`database/`](../database/) folder.

### Application tables

| Table | Purpose | Primary Key | Foreign Keys |
|-------|---------|-------------|--------------|
| `quiz_api_quiz` | Quiz metadata (title, description, difficulty, duration, active flag, timestamps) | `id` | — |
| `quiz_api_question` | MCQ content (prompt, 4 options, correct option, explanation, order) | `id` | `quiz_id → quiz_api_quiz.id` (CASCADE) |
| `quiz_api_quizattempt` | Student submissions (name, JSON responses, score, total) | `id` | `quiz_id → quiz_api_quiz.id` (CASCADE) |

### Authentication tables (Django built-ins)

| Table | Purpose |
|-------|---------|
| `auth_user` | User accounts; `username` unique; password hashed with PBKDF2 |
| `auth_group` | Role groups, seeded with `teacher` and `student` |
| `auth_user_groups` | User↔Group (M:N) — assigns a role at registration |
| `token_blacklist_outstandingtoken` | Issued JWT refresh tokens (simplejwt) |
| `token_blacklist_blacklistedtoken` | Refresh tokens invalidated on logout/rotation |

### Relationships

```
QUIZ (1) ────< QUESTION (M)        ON DELETE CASCADE
QUIZ (1) ────< QUIZATTEMPT (M)     ON DELETE CASCADE
USER (1) ────1 AUTHTOKEN
USER (M) >───< GROUP (M)
```

### Validation (multi-layer)

- **Database:** `NOT NULL`, auto-increment PKs, FKs with `ON DELETE CASCADE`,
  `CHECK (correct_option IN ('A','B','C','D'))`.
- **Model:** field types, `max_length`, defaults, `choices` on `correct_option`.
- **Serializer/API:** payload validation, unique-username check, required fields,
  integer checks on `question_count` / `duration_minutes`.

**References:** ER diagram → [`diagrams/CSE4204-8D-T04_ER-DIAGRAM.md`](../diagrams/CSE4204-8D-T04_ER-DIAGRAM.md) ·
Reference DDL → [`database/schema.sql`](../database/schema.sql) ·
Architecture → [`docs/DATABASE_ARCHITECTURE.md`](../docs/DATABASE_ARCHITECTURE.md)

---

## 5. Implemented APIs

Base URL (local): `http://127.0.0.1:8000/api`

### Authentication

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/register/` | Public | Register a user and assign `teacher`/`student`; returns JWT `access` + `refresh` |
| POST | `/auth/login/` | Public | Authenticate; returns JWT `access` + `refresh` |
| POST | `/auth/token/refresh/` | Public (valid refresh) | Exchange a refresh token for a new access token |
| POST | `/auth/logout/` | Authenticated | Blacklist the supplied `refresh` token |

### Quizzes

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/quizzes/` | Teacher/Student | List quizzes (with `question_count`) |
| POST | `/quizzes/` | Teacher | Create a quiz |
| GET | `/quizzes/{id}/` | Teacher/Student | Retrieve a quiz |
| PUT/PATCH | `/quizzes/{id}/` | Teacher | Update a quiz |
| DELETE | `/quizzes/{id}/` | Teacher | Delete a quiz |

### Questions

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/quizzes/{quiz_id}/questions/` | Teacher | List full questions for a quiz |
| POST | `/quizzes/{quiz_id}/questions/` | Teacher | Add a question to a quiz |
| GET | `/questions/` | Teacher | List questions (filter `?quiz=<id>`) |
| GET/PUT/PATCH/DELETE | `/questions/{id}/` | Teacher | Manage a single question |
| GET | `/quizzes/{quiz_id}/student-questions/` | Teacher/Student | Student-safe questions (no answers) |

### Attempts & scoring

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/quizzes/{quiz_id}/submit/` | Student | Submit answers; auto-scored; stores an attempt |
| GET | `/quizzes/{quiz_id}/attempts/` | Teacher | List attempts for a quiz |

### Documents & AI

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/documents/parse/` | Teacher | Upload a PDF/TXT/MD/CSV/JSON and extract text |
| POST | `/ai/generate-quiz/` | Teacher | Generate a quiz via Gemini/Claude and persist it |

**Full request/response examples:** [`docs/BACKEND_API_REFERENCE.md`](../docs/BACKEND_API_REFERENCE.md)

---

## 6. Authentication Workflow

The system uses **JWT authentication** (`djangorestframework-simplejwt`) with
**role-based access control** via Django Groups (`teacher`, `student`). Each
login/registration issues a short-lived **access** token and a longer-lived
**refresh** token; the user's role is embedded as a claim inside the JWT.

- Access token lifetime: **60 minutes**
- Refresh token lifetime: **1 day** (rotates on refresh; old token blacklisted)

```
Registration
  Client → POST /auth/register/ {username, email, password, role}
         → password hashed (PBKDF2) and user created
         → user added to the "teacher" or "student" group
         → JWT access + refresh pair generated and returned

Login
  Client → POST /auth/login/ {username, password}
         → credentials verified (authenticate())
         → 200 + {access, refresh}   (or 401 on bad credentials)

Authenticated request
  Client → any protected endpoint with header:
           Authorization: Bearer <access>
         → JWTAuthentication validates the signature + expiry and resolves the user
         → custom permission classes check the role
         → 200/201 if allowed · 403 if wrong role · 401 if no/invalid/expired token

Refresh
  Client → POST /auth/token/refresh/ {refresh}
         → 200 + new {access} (and rotated refresh)   (or 401 if invalid/blacklisted)

Logout
  Client → POST /auth/logout/ {refresh}  (with Bearer access header)
         → server blacklists the refresh token so it can no longer mint access tokens
```

**Role rules** (enforced in [`backend/quiz_api/permissions.py`](../backend/quiz_api/permissions.py)):

- **Teacher:** create/update/delete quizzes & questions, parse documents,
  generate AI quizzes, view attempts.
- **Student:** view student-safe questions, submit attempts.
- All protected endpoints require a valid token.

**Security notes:** passwords are never stored in plain text; Django's password
validators (minimum length, common-password, numeric, similarity) are enabled;
the secret key, DB credentials, and AI keys are read from environment variables.

---

## 7. Current Development Progress

| Area | Status |
|------|--------|
| Backend project setup (Django + DRF) | ✅ Complete |
| Database schema, migrations, seed data | ✅ Complete |
| Authentication — JWT (register, login, refresh, logout/blacklist, hashing) | ✅ Complete |
| Role-based authorization (teacher/student) | ✅ Complete |
| Core APIs (quizzes, questions, attempts, scoring) | ✅ Complete |
| Document parsing (PDF/TXT/MD/CSV/JSON) | ✅ Complete |
| AI quiz generation (Gemini + Claude) | ✅ Implemented (needs API key to run live) |
| Database connectivity (MySQL) | ✅ Complete |
| Error handling & validation | ✅ Complete |
| API testing (Postman + scripted smoke test) | ✅ Complete |
| Frontend | 🔜 Separate upcoming project |
| Per-teacher quiz ownership (`created_by`) | 🟡 Planned (per SRS) |
| Production hardening (WSGI server, throttling) | 🟡 Planned |

### Error handling implemented

- Invalid input → `400 Bad Request` with a descriptive `detail` message.
- Missing/invalid token → `401 Unauthorized`.
- Wrong role → `403 Forbidden`.
- AI provider key not configured → `503 Service Unavailable` (no crash).
- AI returns fewer questions than requested → `502 Bad Gateway`.

---

## 8. Screenshots of API Testing

All screenshots below are generated automatically by
[`backend/capture_screenshots.py`](../backend/capture_screenshots.py), which runs
the same end-to-end suite as [`backend/system_check.py`](../backend/system_check.py)
and renders one Postman-style image per step (request on top, response below, with
a PASS/FAIL/SKIP pill). To regenerate them against a live server:

```bash
cd backend
python manage.py migrate
python manage.py runserver          # terminal 1
python capture_screenshots.py       # terminal 2 → writes ../documentation/api_screenshots/
```

### 8.1 Test summary — 28 / 28 passed

The full suite runs **28 steps** covering connectivity, authentication,
role-based permissions, CRUD, auto-scoring, document parsing, AI generation, and
JWT refresh/blacklist. Latest run: **PASS 28 · FAIL 0 · SKIP 0**.

![API test summary — 28 passed, 0 failed, 0 skipped](api_screenshots/00_summary.png)

### 8.2 Database tables

MySQL/phpMyAdmin view of the application and authentication tables
(`quiz_api_quiz`, `quiz_api_question`, `quiz_api_quizattempt`, `auth_user`,
`auth_group`, and the simplejwt token-blacklist tables).

![Database collections / tables](database-collections-tables.png)

### 8.3 Connectivity

Protected route rejects a request that carries no token (`401 Unauthorized`).

![Protected route without a token → 401](api_screenshots/01_connectivity-protected-route-without-a-token.png)

### 8.4 Authentication

Registration of a teacher and a student (each returns a JWT `access` + `refresh`
pair), duplicate-username rejection (`400`), and login with correct vs. wrong
password (`200` vs. `401`).

![Register teacher → 201 + JWT](api_screenshots/02_auth-register-teacher.png)
![Register student → 201 + JWT](api_screenshots/03_auth-register-student.png)
![Duplicate username rejected → 400](api_screenshots/04_auth-duplicate-username-rejected.png)
![Login with correct password → 200](api_screenshots/05_auth-login-with-correct-password.png)
![Login with wrong password → 401](api_screenshots/06_auth-login-with-wrong-password.png)

### 8.5 Role-based permissions

A student and an anonymous caller are both blocked from creating a quiz
(`403` / `401`), proving role enforcement.

![Student cannot create a quiz → 403](api_screenshots/07_permissions-student-cannot-create-a-quiz.png)
![Anonymous cannot create a quiz → 401](api_screenshots/08_permissions-anonymous-cannot-create-a-quiz.png)

### 8.6 Quizzes & questions (teacher CRUD)

Create a quiz, add three questions (answers A/B/C), list quizzes, retrieve one
with its `question_count`, and update the title via `PATCH`.

![Create quiz → 201](api_screenshots/09_quizzes-create-quiz.png)
![Add question 1 (answer A) → 201](api_screenshots/10_questions-add-question-1-answer-a.png)
![Add question 2 (answer B) → 201](api_screenshots/11_questions-add-question-2-answer-b.png)
![Add question 3 (answer C) → 201](api_screenshots/12_questions-add-question-3-answer-c.png)
![List quizzes → 200](api_screenshots/13_quizzes-list-quizzes.png)
![Retrieve quiz with question_count → 200](api_screenshots/14_quizzes-retrieve-quiz-question-count.png)
![Update quiz title (PATCH) → 200](api_screenshots/15_quizzes-update-quiz-title-patch.png)

### 8.7 Student flow & auto-scoring

Student fetches answer-free questions, submits an attempt that is auto-scored
(2/3), the teacher reads back the attempts, and a student is blocked from viewing
attempts (`403`).

![Student-safe questions (answers hidden)](api_screenshots/16_student-student-safe-questions-answers-hidden.png)
![Submit attempt → scored 2/3](api_screenshots/17_student-submit-attempt-expect-2-3.png)
![Teacher views attempts → 200](api_screenshots/18_student-teacher-views-attempts.png)
![Student cannot view attempts → 403](api_screenshots/19_student-student-cannot-view-attempts.png)

### 8.8 Documents & AI

Teacher uploads and parses a `.txt` document; a student is blocked from the
parse endpoint (`403`); and the AI endpoint generates a quiz.

![Teacher parses an uploaded .txt → 200](api_screenshots/20_documents-teacher-parses-an-uploaded-txt.png)
![Student cannot parse documents → 403](api_screenshots/21_documents-student-cannot-parse-documents.png)
![Generate quiz with AI](api_screenshots/22_ai-generate-quiz-with-ai.png)

### 8.9 JWT lifecycle (refresh, logout, blacklist)

Refresh exchanges a valid refresh token for a new access token; logout without a
refresh token is rejected; logout blacklists the refresh token; and a
blacklisted refresh is then refused.

![Refresh access token → 200](api_screenshots/23_jwt-refresh-access-token.png)
![Logout without a refresh token → 400](api_screenshots/24_jwt-logout-without-a-refresh-token.png)
![Logout blacklists refresh token → 200](api_screenshots/25_jwt-logout-blacklist-refresh-token.png)
![Blacklisted refresh is rejected → 401](api_screenshots/26_jwt-blacklisted-refresh-is-rejected.png)

### 8.10 Cleanup

The suite deletes the quizzes it created so the run is repeatable and leaves no
test data behind.

![Delete quiz → 204](api_screenshots/27_cleanup-delete-quiz-id-15.png)
![Delete quiz → 204](api_screenshots/28_cleanup-delete-quiz-id-16.png)

---

## 9. GitHub Repository

- **Repository:** https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR
- **Default branch:** `main`
- **Contributors:** all four team members listed in Section 2.
- **Workflow:** regular commits with meaningful messages (e.g. *"AI Integration"*,
  *"Updating Documenting & Separating AI integration from original backend"*),
  organized folder structure, and documentation kept in sync with the code.

---

## Appendix — How to run and test

```bash
# 1. Create the database
mysql -u root -p -e "CREATE DATABASE smart_quiz_generator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2. Install dependencies
cd backend
pip install -r requirements.txt

# 3. Configure backend/.env (DB credentials, secret key, optional AI keys)

# 4. Apply migrations (creates tables + teacher/student roles)
python manage.py migrate

# 5. (Optional) seed sample data
mysql -u root -p smart_quiz_generator < ../database/seed_data.sql

# 6. Run the server
python manage.py runserver

# 7. Test — import postman/ collection, OR run the scripted smoke test:
python manual_api_test.py
```
