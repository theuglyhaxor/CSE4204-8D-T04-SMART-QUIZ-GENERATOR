# Database architecture

This document summarizes the database schema used by the Django backend.

## Overview

The schema is created and owned by **Django migrations** (`python manage.py migrate`). It runs on
either backend, selected with the `DB_ENGINE` environment variable:

- **SQLite** (`DB_ENGINE=sqlite`, the default) — zero setup, used for development and demos.
- **MySQL / MariaDB** (`DB_ENGINE=mysql`) — the deployment target documented in
  [`database/schema.sql`](../database/schema.sql).

The models are identical either way; only the connection differs.

It stores:

- Django auth data for users, groups and permissions
- quiz data: quizzes, questions and attempts
- role assignments for teacher and student access
- the JWT refresh-token blacklist (logout / rotation)

## Core tables

### `quiz_api_quiz`

Stores quiz metadata.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | integer PK | Auto-increment |
| `title` | varchar(255) | Quiz title |
| `description` | text | Quiz description |
| `difficulty` | varchar(50) | `Easy`, `Medium` or `Hard` |
| `duration_minutes` | integer | Duration in minutes |
| `is_active` | boolean | **Defaults to `false` (draft).** Students only see quizzes where this is `true`. A teacher publishes by setting it. |
| `created_by_id` | integer FK, nullable | References `auth_user.id` — the **owning teacher**. Only the owner may update or delete the quiz. Nullable so rows seeded before ownership existed stay valid. `ON DELETE SET NULL`. |
| `created_at` | datetime | Created timestamp |
| `updated_at` | datetime | Updated timestamp |

### `quiz_api_question`

Stores the questions for each quiz.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | integer PK | Auto-increment |
| `quiz_id` | integer FK | References `quiz_api_quiz.id` |
| `prompt` | text | Question text |
| `option_a` | varchar(255) | Option A |
| `option_b` | varchar(255) | Option B |
| `option_c` | varchar(255) | Option C |
| `option_d` | varchar(255) | Option D |
| `correct_option` | varchar(1) | One of `A`, `B`, `C`, `D` |
| `explanation` | text | Explanation for the correct answer |
| `order` | integer | Display order within the quiz |

### `quiz_api_quizattempt`

Stores student submissions and scores.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | integer PK | Auto-increment |
| `quiz_id` | integer FK | References `quiz_api_quiz.id`, `ON DELETE CASCADE` |
| `student_id` | integer FK, nullable | References `auth_user.id` — the **authenticated submitter**. Authorisation is checked against this column: `GET /api/attempts/me/` filters on it, so a student can only ever read their own attempts. `ON DELETE CASCADE`. |
| `student_name` | varchar(255) | Denormalised display label, derived **server-side** from the authenticated user. It is deliberately **not** read from the request body — otherwise a student could file an attempt under someone else's name. |
| `responses` | json | Per-question answer payload: `question`, `selected_option`, `correct_option`, `is_correct`, `explanation` |
| `score` | integer | Correct answers |
| `total` | integer | Total questions in the quiz |
| `created_at` | datetime | Created timestamp |

## Auth and RBAC tables

Authentication is **JWT** (`djangorestframework-simplejwt`) over Django's built-in auth tables.
Access and refresh tokens are signed and stateless; the only auth state in the database is the
refresh-token blacklist used for logout and rotation.

### Django auth tables

- `auth_user` — accounts (unique `username`, PBKDF2-hashed password)
- `auth_group` — the role groups: `teacher` and `student`
- `auth_user_groups` — M:N junction assigning a role to a user
- `auth_permission`, `auth_user_user_permissions` — Django built-ins (unused by the app's RBAC)

A user's role is read from their group membership — see `get_user_role()` in
[`backend/quiz_api/permissions.py`](../backend/quiz_api/permissions.py) — and is also embedded as a
`role` claim in the JWT.

### JWT blacklist tables

- `token_blacklist_outstandingtoken` — every issued refresh token
- `token_blacklist_blacklistedtoken` — refresh tokens invalidated by logout or rotation

> There is **no** `authtoken_token` table. The project does not use DRF's `TokenAuthentication`.

## Relationships

- `auth_user` -> `quiz_api_quiz` : one-to-many (via `created_by_id` — a teacher owns their quizzes)
- `quiz_api_quiz` -> `quiz_api_question` : one-to-many (CASCADE)
- `quiz_api_quiz` -> `quiz_api_quizattempt` : one-to-many (CASCADE)
- `auth_user` -> `quiz_api_quizattempt` : one-to-many (via `student_id` — a student owns their attempts)
- `auth_user` -> `auth_group` : many-to-many (role assignment)
- `auth_user` -> `token_blacklist_outstandingtoken` : one-to-many (issued JWT refresh tokens)

## Role usage

The backend assigns users to the `teacher` or `student` group during registration.

- **`teacher`** — create and manage *their own* quizzes and questions, generate quizzes with AI,
  parse documents, export PDFs (with the answer key), and read every attempt at their quizzes.
- **`student`** — list *published* quizzes, read student-safe questions (answers stripped), submit
  answers, export the handout PDF, and read *only their own* attempts.

## Notes

- The schema is generated by Django migrations under `backend/quiz_api/migrations/`
- `DB_ENGINE` selects SQLite (default) or MySQL; the models are identical on both
- The seed script at `database/seed_data.sql` is for local development
- The document-parsing endpoint does **not** persist uploaded content; it returns the parsed text in the response

## Example schema diagram

```text
auth_user
  |-- auth_user_groups --> auth_group        (role: teacher / student)
  |-- token_blacklist_outstandingtoken       (JWT refresh tokens)
  |-- quiz_api_quiz          (created_by_id  — quizzes this teacher owns)
  |-- quiz_api_quizattempt   (student_id     — attempts this student submitted)

quiz_api_quiz
  |-- quiz_api_question      (quiz_id, CASCADE)
  |-- quiz_api_quizattempt   (quiz_id, CASCADE)
```
