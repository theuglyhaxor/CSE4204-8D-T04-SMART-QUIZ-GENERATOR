-- =====================================================================
-- SMART QUIZ GENERATOR — Database Schema (Reference DDL)
-- CSE4204-8D-T04 | Batch 8D | Team 04
-- =====================================================================
--
-- This file documents the database schema for reference and review.
--
-- IMPORTANT: In normal operation the schema is created and maintained by
-- Django migrations, NOT by running this file. Use:
--
--     python manage.py migrate
--
-- The DDL below mirrors what those migrations produce (Django 4.2 on MySQL
-- 5.7+/MariaDB 10.3+) so reviewers can inspect tables, primary keys, foreign
-- keys, and relationships without standing up the app. It is also useful for
-- recreating the application tables by hand on a fresh MySQL instance.
--
-- Engine: InnoDB (required for foreign keys)
-- Charset: utf8mb4
-- =====================================================================

CREATE DATABASE IF NOT EXISTS smart_quiz_generator
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE smart_quiz_generator;

-- ---------------------------------------------------------------------
-- Authentication & roles
-- ---------------------------------------------------------------------
-- Authentication reuses Django's built-in auth tables plus the JWT blacklist
-- tables. They are created by `python manage.py migrate`
-- (apps: auth, rest_framework_simplejwt.token_blacklist). They are listed here
-- for completeness only — do NOT hand-create them; let Django own them.
--
--   auth_user                            -- user accounts (username UK, hashed password)
--   auth_group                           -- role groups: 'teacher' / 'student'
--   auth_user_groups                     -- M:N junction (user_id, group_id)
--   token_blacklist_outstandingtoken     -- issued JWT refresh tokens
--   token_blacklist_blacklistedtoken     -- refresh tokens invalidated by logout
--
-- Authentication is JWT (djangorestframework-simplejwt): access + refresh
-- tokens are signed and stateless. The only auth state kept in the DB is the
-- refresh-token blacklist used for logout / rotation.
--
-- Password storage: Django hashes passwords with PBKDF2-SHA256 by default.
-- Plain-text passwords are never stored.
-- ---------------------------------------------------------------------

-- =====================================================================
-- Application tables (owned by the quiz_api Django app)
-- =====================================================================

-- ---------------------------------------------------------------------
-- QUIZ — quiz metadata and configuration
--
-- created_by  : the teacher who owns the quiz. Only the owner may update or
--               delete it. NULL-able so pre-existing seeded rows (created before
--               ownership was introduced) remain valid and editable.
-- is_active   : FALSE = draft (invisible to students), TRUE = published.
--               New quizzes default to draft so an empty quiz is never exposed.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quiz_api_quiz (
    id               INTEGER       NOT NULL AUTO_INCREMENT,
    title            VARCHAR(255)  NOT NULL,
    description      LONGTEXT      NOT NULL,
    difficulty       VARCHAR(50)   NOT NULL DEFAULT 'Medium',
    duration_minutes INTEGER UNSIGNED NOT NULL DEFAULT 5,
    is_active        TINYINT(1)    NOT NULL DEFAULT 0,
    created_by_id    INTEGER       NULL,
    created_at       DATETIME(6)   NOT NULL,
    updated_at       DATETIME(6)   NOT NULL,
    PRIMARY KEY (id),
    KEY quiz_api_quiz_created_by_id_idx (created_by_id),
    CONSTRAINT quiz_api_quiz_created_by_id_fk
        FOREIGN KEY (created_by_id) REFERENCES auth_user (id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- QUESTION — MCQ content linked to a quiz (1:M, ON DELETE CASCADE)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quiz_api_question (
    id             INTEGER       NOT NULL AUTO_INCREMENT,
    quiz_id        INTEGER       NOT NULL,
    prompt         LONGTEXT      NOT NULL,
    option_a       VARCHAR(255)  NOT NULL,
    option_b       VARCHAR(255)  NOT NULL,
    option_c       VARCHAR(255)  NOT NULL,
    option_d       VARCHAR(255)  NOT NULL,
    correct_option VARCHAR(1)    NOT NULL,  -- constrained to A/B/C/D in app + CHECK below
    explanation    LONGTEXT      NOT NULL,
    `order`        INTEGER UNSIGNED NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    KEY quiz_api_question_quiz_id_idx (quiz_id),
    CONSTRAINT quiz_api_question_quiz_id_fk
        FOREIGN KEY (quiz_id) REFERENCES quiz_api_quiz (id)
        ON DELETE CASCADE,
    CONSTRAINT quiz_api_question_correct_option_chk
        CHECK (correct_option IN ('A', 'B', 'C', 'D'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- QUIZATTEMPT — student submission with embedded answers (JSON)
-- 1:M from QUIZ (ON DELETE CASCADE). Answers are stored denormalised in
-- the `responses` JSON column (no separate answer table by design).
--
-- student_id   : the authenticated submitter. Authorisation is checked against
--                THIS column — a student may only read their own attempts.
-- student_name : denormalised display label, derived server-side from the
--                authenticated user. It is never taken from the request body.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quiz_api_quizattempt (
    id           INTEGER       NOT NULL AUTO_INCREMENT,
    quiz_id      INTEGER       NOT NULL,
    student_id   INTEGER       NULL,
    student_name VARCHAR(255)  NOT NULL DEFAULT 'Anonymous',
    responses    JSON          NOT NULL,
    score        INTEGER UNSIGNED NOT NULL DEFAULT 0,
    total        INTEGER UNSIGNED NOT NULL DEFAULT 0,
    created_at   DATETIME(6)   NOT NULL,
    PRIMARY KEY (id),
    KEY quiz_api_quizattempt_quiz_id_idx (quiz_id),
    KEY quiz_api_quizattempt_student_id_idx (student_id),
    CONSTRAINT quiz_api_quizattempt_quiz_id_fk
        FOREIGN KEY (quiz_id) REFERENCES quiz_api_quiz (id)
        ON DELETE CASCADE,
    CONSTRAINT quiz_api_quizattempt_student_id_fk
        FOREIGN KEY (student_id) REFERENCES auth_user (id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- Relationship summary
-- =====================================================================
--   USER (1) ──< QUIZ (M)            via quiz_api_quiz.created_by_id      (owner)
--   QUIZ (1) ──< QUESTION (M)        via quiz_api_question.quiz_id
--   QUIZ (1) ──< QUIZATTEMPT (M)     via quiz_api_quizattempt.quiz_id
--   USER (1) ──< QUIZATTEMPT (M)     via quiz_api_quizattempt.student_id  (submitter)
--   USER (1) ──< OUTSTANDINGTOKEN    via token_blacklist_outstandingtoken.user_id
--   USER (M) >──< GROUP (M)          via auth_user_groups
-- =====================================================================
