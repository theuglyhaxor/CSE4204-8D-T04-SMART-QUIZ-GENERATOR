# Database — Smart Quiz Generator

**CSE4204-8D-T04 | Batch 8D | Team 04**

This folder contains the database design artifacts for the Smart Quiz Generator
backend. The live schema is owned by **Django migrations**; the SQL files here
are a human-readable reference and a way to seed test data.

## DBMS

- **MySQL 5.7+ / MariaDB 10.3+** (engine: InnoDB, charset: `utf8mb4`)
- Driver: `PyMySQL` (registered as MySQLdb in `settings.py`)
- Database name: `smart_quiz_generator`

## Files

| File | Purpose |
|------|---------|
| [`schema.sql`](schema.sql) | Reference DDL — tables, primary keys, foreign keys, constraints. Mirrors what `python manage.py migrate` produces. |
| [`seed_data.sql`](seed_data.sql) | Sample quizzes, questions, and attempts for local testing. |
| [`../diagrams/CSE4204-8D-T04_ER-DIAGRAM.md`](../diagrams/CSE4204-8D-T04_ER-DIAGRAM.md) | Full ER diagram (Mermaid) with relationships and notation. |
| [`../docs/DATABASE_ARCHITECTURE.md`](../docs/DATABASE_ARCHITECTURE.md) | Extended schema/architecture write-up. |

## How the schema is created

The schema is **not** created by running `schema.sql` in normal use. Django
migrations are the source of truth:

```bash
# 1. Create the database (once)
mysql -u root -p -e "CREATE DATABASE smart_quiz_generator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2. Apply migrations (creates all tables, keys, and the teacher/student roles)
cd backend
python manage.py migrate

# 3. (Optional) load sample data
mysql -u root -p smart_quiz_generator < ../database/seed_data.sql
```

`schema.sql` is provided so reviewers can read the structure directly, or
recreate the application tables on a fresh MySQL instance without the app.

## Tables

### Application tables (`quiz_api` app)

| Table | Purpose | Primary Key | Foreign Keys |
|-------|---------|-------------|--------------|
| `quiz_api_quiz` | Quiz metadata (title, description, difficulty, duration, active flag, timestamps) | `id` | — |
| `quiz_api_question` | MCQ content (prompt, 4 options, correct option, explanation, order) | `id` | `quiz_id → quiz_api_quiz.id` (CASCADE) |
| `quiz_api_quizattempt` | Student submissions (name, JSON responses, score, total) | `id` | `quiz_id → quiz_api_quiz.id` (CASCADE) |

### Authentication tables (Django built-ins + JWT blacklist)

| Table | Purpose | Notes |
|-------|---------|-------|
| `auth_user` | User accounts | `username` unique; password hashed with **PBKDF2-SHA256** |
| `auth_group` | Role groups | Seeded with `teacher` and `student` (migration `0002_create_roles`) |
| `auth_user_groups` | User↔Group junction (M:N) | Assigns each user a role at registration |
| `token_blacklist_outstandingtoken` | Issued JWT refresh tokens | Created by `simplejwt` token_blacklist app |
| `token_blacklist_blacklistedtoken` | Refresh tokens invalidated by logout/rotation | Logout blacklists the refresh token |

> **Auth is JWT** (`djangorestframework-simplejwt`): access + refresh tokens are
> signed and stateless. The only auth state stored in the DB is the refresh-token
> blacklist (used for logout and refresh rotation).

## Relationships

```
QUIZ (1) ────< QUESTION (M)        quiz_api_question.quiz_id   (ON DELETE CASCADE)
QUIZ (1) ────< QUIZATTEMPT (M)     quiz_api_quizattempt.quiz_id (ON DELETE CASCADE)
USER (1) ────< OUTSTANDINGTOKEN    token_blacklist_outstandingtoken.user_id
USER (M) >───< GROUP (M)           auth_user_groups
```

## Validation

Validation is enforced at multiple layers:

- **Database:** `NOT NULL` constraints, `AUTO_INCREMENT` primary keys, foreign keys
  with `ON DELETE CASCADE`, and a `CHECK` that `correct_option ∈ {A,B,C,D}`.
- **ORM / model:** field types, `max_length`, `default`s, and `choices` on
  `correct_option` (see [`backend/quiz_api/models.py`](../backend/quiz_api/models.py)).
- **API / serializer:** DRF serializers validate request payloads, unique username
  on registration, and required fields (see
  [`backend/quiz_api/serializers.py`](../backend/quiz_api/serializers.py)).

## Design note: denormalised answers

Student answers are stored in the `responses` **JSON** column of
`quiz_api_quizattempt` rather than in a separate answer table. Each attempt is
self-contained:

```json
[
  { "question": 1, "selected_option": "B", "correct_option": "B", "is_correct": true },
  { "question": 2, "selected_option": "A", "correct_option": "C", "is_correct": false }
]
```
