<!--
  CSE4204-8D-T04 — SYSTEM DESIGN & SOFTWARE ARCHITECTURE
  Single-file master document. Export to PDF as CSE4204-8D-T04_SystemDesign.pdf
  (VS Code "Markdown PDF" extension, or the headless-Chromium build, render the
  mermaid diagrams below). The embedded <style> block controls print layout:
  it keeps diagrams whole, caps tall images to one page, prevents orphaned
  headings, and removes the blank pages the previous export produced.
-->

<style>
/* ---- Print / PDF layout ------------------------------------------------ */
@page { size: A4; margin: 18mm 16mm; }

body { line-height: 1.5; }

/* Keep headings attached to the content that follows them */
h1, h2, h3, h4 { page-break-after: avoid; break-after: avoid; }
/* Never split these blocks across a page boundary */
table, pre, blockquote, figure { page-break-inside: avoid; break-inside: avoid; }

hr { border: 0; border-top: 1px solid #d8dee4; margin: 1.4em 0; }

/* Diagrams ---------------------------------------------------------------- */
figure { margin: 0.8em 0 1.1em; text-align: center; }
figure img { max-width: 100%; height: auto; }
figcaption { font-size: 0.85em; color: #57606a; margin-top: 0.4em; }

/* Tall portrait flowcharts: cap height so heading + image fit one page */
figure.tall img { width: auto; max-width: 100%; max-height: 22cm; }

/* Mermaid diagrams render as inline SVG; keep them whole and centred */
.mermaid { text-align: center; page-break-inside: avoid; break-inside: avoid; margin: 0.6em 0; }
.mermaid svg { max-width: 100%; max-height: 22cm; height: auto; }
pre:has(.mermaid) { background: none; border: none; padding: 0; }

/* ---- Cover page -------------------------------------------------------- */
.cover { text-align: center; }
.cover-logo { width: 78%; max-width: 460px; margin: 18mm auto 6mm; }
.cover-dept { font-size: 1.15em; font-weight: 600; color: #24292f; letter-spacing: 0.3px; }
.cover-title { font-size: 2.5em; font-weight: 700; margin: 8px 0 4px; letter-spacing: 1px; border: 0; }
.cover-sub { font-size: 1.05em; color: #57606a; font-style: italic; }
.cover-hr { width: 60%; margin: 12px auto 16px; border-top: 2px solid #24292f; }
.cover-abstract { max-width: 80%; margin: 0 auto 14px; color: #3a3f45; }
.cover-meta { margin: 8px auto 18px; border-collapse: collapse; font-size: 0.98em; }
.cover-meta td { padding: 4px 14px; border: 0; }
.cover-meta td:first-child { text-align: right; font-weight: 600; color: #57606a; }
.cover-meta td:last-child { text-align: left; }
.cover-parties { margin: 10mm auto 0; border-collapse: collapse; width: 92%; }
.cover-parties td { vertical-align: top; width: 50%; padding: 0 12px; border: 0; line-height: 1.45; }
.cover-parties .label { font-weight: 700; color: #24292f; border-bottom: 1px solid #d8dee4; padding-bottom: 3px; margin-bottom: 6px; display: block; }
.cover-date { margin-top: 14mm; font-style: italic; color: #57606a; }
</style>

<div class="cover">

<img class="cover-logo" src="image.png" alt="Northern University of Business and Technology, Khulna" />

<div class="cover-dept">Department of Computer Science and Engineering</div>

<div class="cover-title">SMART QUIZ GENERATOR</div>

<div class="cover-sub">System Design &amp; Software Architecture Document</div>

<hr class="cover-hr" />

<p class="cover-abstract">An AI-assisted, role-based quiz management system that lets teachers create quizzes — manually or generated from documents via Google Gemini — and lets students take and be scored on them through a secure REST API.</p>

<table class="cover-meta">
<tr><td>Course</td><td>CSE4204 — Mobile Computing Lab</td></tr>
<tr><td>Submission</td><td>System Design Document</td></tr>
<tr><td>Team ID</td><td>CSE4204-8D-T04 &nbsp;·&nbsp; Section 8D</td></tr>
</table>

<table class="cover-parties">
<tr>
<td>
<span class="label">Submitted To</span>
Md. Riaz Mahmud<br/>
Assistant Professor, Dept. of CSE<br/>
Northern University of Business and Technology, Khulna
</td>
<td>
<span class="label">Submitted By</span>
Team CSE4204-8D-T04 (Section 8D)<br/>
MD Rohan · Sharmin Nahar Tumpa<br/>
Pial Tarofdar · Sanjana Athoy
</td>
</tr>
</table>

<div class="cover-date">Submission Date: 15 June 2026</div>

</div>

<div style="page-break-after: always;"></div>

## Table of Contents

1. [Team Information](#1-team-information)
2. [Project Information](#2-project-information)
3. [System Architecture Diagram](#3-system-architecture-diagram)
4. [ER Diagram (Database Design)](#4-er-diagram-database-design)
5. [Use Case Diagram](#5-use-case-diagram)
6. [Activity Diagrams](#6-activity-diagrams)
7. [API Design](#7-api-design)
8. [AI Integration Workflow](#8-ai-integration-workflow)
9. [References](#9-references)

<div style="page-break-after: always;"></div>

## 1. Team Information

**Team ID:** CSE4204-8D-T04

| No. | Name | Student ID | Role / Responsibility |
|-----|------|-----------|------------------------|
| 1 | MD Rohan | 11220320958 | Backend Developer, Full Stack Development |
| 2 | Sharmin Nahar Tumpa | 11220320962 | AI Integration |
| 3 | Pial Tarofdar | 11220320965 | Frontend Developer |
| 4 | Sanjana Athoy | 11220320953 | Overall Technical Help |

---

## 2. Project Information

**Project Title:** Smart Quiz Generator

**Overview:** A role-based quiz platform with a Django REST backend. Teachers
create and manage quizzes and questions, upload documents, and use Google
Gemini to auto-generate validated multiple-choice questions. Students take
quizzes without seeing answers and receive instant, server-calculated scores.

**Technology Stack:**

| Layer | Technology |
|-------|-----------|
| Frontend | React.js (developed separately, consumes the API) |
| Backend API | Django + Django REST Framework (Python 3.9+) |
| Database | MySQL 5.7+ / MariaDB 10.3+ |
| Authentication | DRF Token authentication + Django Groups (roles) |
| AI Service | Google Gemini (`gemini-2.5-flash`, default) or Anthropic Claude (`claude-opus-4-8`) — see `backend/ai_integration/` |
| File Parsing | pypdf + UTF-8 text decoding (PDF/TXT/MD/CSV/JSON) |
| Deployment (planned) | Gunicorn + Nginx, Railway/Render |

**Scope (from SRS):** quiz CRUD, question management, AI generation, document
parsing, role-based access (teacher/student), token auth, attempt tracking and
scoring. Out of scope: production message queue, mobile app, real-time
notifications, payments.

> **Note:** Diagrams reflect the **intended SRS design**. Items planned but not
> yet in code are tagged **🟡 planned** (e.g., quiz ownership via `created_by`,
> `/auth/logout/`, document→AI chaining).

---

## 3. System Architecture Diagram

The system is organized into five layers: Client, API Gateway, Application
(Django services), Data, and External Services.

```mermaid
graph TB
    subgraph Client["CLIENT LAYER"]
        WEB["Web Browser - React.js"]
        MOBILE["Mobile App (optional)"]
    end
    subgraph Gateway["API GATEWAY"]
        NGINX["Nginx - Reverse Proxy, HTTPS, Load Balancing"]
    end
    subgraph AppLayer["APPLICATION LAYER - Django REST Framework"]
        AUTH["Authentication - Token + Roles"]
        QUIZ["Quiz Service - CRUD"]
        QUESTION["Question Service"]
        SCORING["Scoring Service"]
        PARSER["Document Parser"]
        AICLIENT["AI Client (Gemini)"]
        PERM["Permission System (RBAC)"]
    end
    subgraph DataLayer["DATA LAYER"]
        MYSQL[("MySQL / MariaDB")]
        CACHE[("Redis (optional)")]
    end
    subgraph External["EXTERNAL SERVICES"]
        GEMINI["Google Gemini API"]
    end

    WEB -->|HTTPS/REST| NGINX
    MOBILE -->|HTTPS/REST| NGINX
    NGINX --> AUTH
    NGINX --> QUIZ
    NGINX --> QUESTION
    NGINX --> SCORING
    NGINX --> PARSER
    NGINX --> AICLIENT
    AUTH --> PERM
    QUIZ --> MYSQL
    QUESTION --> MYSQL
    SCORING --> MYSQL
    AICLIENT -->|prompt| GEMINI
    GEMINI -->|questions JSON| AICLIENT
    AUTH -.cache.-> CACHE

    style Client fill:#e1f5ff
    style Gateway fill:#fff3e0
    style AppLayer fill:#f3e5f5
    style DataLayer fill:#e8f5e9
    style External fill:#fce4ec
```

**Request flow:** `Client → HTTPS → Nginx → Django service → MySQL → response`.
**AI flow:** `Teacher input → AI Client → Gemini → validated questions → DB`.
Full detail: [Architecture Diagram on GitHub](https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/diagrams/CSE4204-8D-T04_ARCHITECTURE-DIAGRAM.md).

---

## 4. ER Diagram (Database Design)

`PK` = Primary Key · `FK` = Foreign Key · `UK` = Unique Key · 🟡 = planned.

```mermaid
erDiagram
    USER }o--o{ GROUP : "belongs to"
    USER ||--o| AUTHTOKEN : "has"
    USER ||--o{ QUIZ : "creates (planned)"
    QUIZ ||--o{ QUESTION : "contains"
    QUIZ ||--o{ QUIZATTEMPT : "receives"

    USER {
        int id PK
        string username UK
        string email
        string password "hashed (PBKDF2)"
        boolean is_active
        datetime date_joined
    }
    GROUP {
        int id PK
        string name UK "teacher or student"
    }
    AUTHTOKEN {
        string key PK
        int user_id FK
        datetime created
    }
    QUIZ {
        int id PK
        int created_by FK "teacher (PLANNED)"
        string title
        text description
        string difficulty
        int duration_minutes
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    QUESTION {
        int id PK
        int quiz_id FK
        text prompt
        string option_a
        string option_b
        string option_c
        string option_d
        string correct_option "A-D"
        text explanation
        int order
    }
    QUIZATTEMPT {
        int id PK
        int quiz_id FK
        string student_name
        json responses "embedded answers"
        int score
        int total
        datetime created_at
    }
```

Student answers are stored inside `QuizAttempt.responses` as JSON (no separate
answer table), per SRS FR-30. Full detail and the corrections log:
[ER Diagram on GitHub](https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/diagrams/CSE4204-8D-T04_ER-DIAGRAM.md).

---

## 5. Use Case Diagram

Actors: **Teacher**, **Student**, and the external **Gemini AI** service.

```mermaid
graph TB
    subgraph System["Smart Quiz Generator"]
        UC1["Register / Login"]
        UC2["Create Quiz"]
        UC3["Add / Manage Questions"]
        UC4["Upload Document"]
        UC5["Generate Questions (AI)"]
        UC6["View Active Quizzes"]
        UC7["Take Quiz"]
        UC8["Submit Quiz"]
        UC9["View Score"]
        UC10["Review Submissions"]
        UC11["Set Quiz Active/Inactive"]
        UC12["Delete Quiz"]
    end
    Teacher["Teacher"]
    Student["Student"]
    Gemini["Gemini AI"]

    Teacher --> UC1
    Teacher --> UC2
    Teacher --> UC3
    Teacher --> UC4
    Teacher --> UC5
    Teacher --> UC10
    Teacher --> UC11
    Teacher --> UC12
    Student --> UC1
    Student --> UC6
    Student --> UC7
    Student --> UC8
    Student --> UC9
    UC5 -.->|AI call| Gemini
    UC7 -.->|include| UC6
    UC8 -.->|calculates| UC9
```

Full descriptions: [Use Case Diagram on GitHub](https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/diagrams/CSE4204-8D-T04_USE_CASE_DIAGRAM.md).

---

## 6. Activity Diagrams

Two primary workflows are shown below. Each diagram is kept whole on its own
page; additional workflows (Registration/Login, Document Parsing) are linked at
the end of this section.

<figure class="tall">

![AI Question Generation activity diagram](image-1.png)

<figcaption><strong>6.1</strong> — AI Question Generation (major feature)</figcaption>

</figure>

<figure class="tall">

![Student takes and submits a quiz activity diagram](image-2.png)

<figcaption><strong>6.2</strong> — Student Takes &amp; Submits a Quiz</figcaption>

</figure>

Additional workflows (Registration/Login, Document Parsing) and full
decision branches: [Activity Diagrams on GitHub](https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/diagrams/CSE4204-8D-T04_ACTIVITY-DIAGRAM.md).

---

## 7. API Design

Base URL (dev): `http://127.0.0.1:8000/api/` · Auth header: `Authorization: Bearer <access_token>` (JWT).

| Group | Method & Endpoint | Role | Purpose |
|-------|-------------------|------|---------|
| Auth | POST `/auth/register/` | public | Create user + issue token |
| Auth | POST `/auth/login/` | public | Authenticate, return token |
| Auth | POST `/auth/logout/` | token | Invalidate token |
| Quiz | GET `/quizzes/` | teacher/student | List quizzes |
| Quiz | POST `/quizzes/` | teacher | Create quiz |
| Quiz | GET/PUT/PATCH/DELETE `/quizzes/{id}/` | teacher | Retrieve/update/delete quiz |
| Question | GET/POST `/quizzes/{id}/questions/` | teacher | List / add questions |
| Question | GET/PUT/PATCH/DELETE `/questions/{id}/` | teacher | Manage a question |
| Student | GET `/quizzes/{id}/student-questions/` | teacher/student | Questions without answers |
| Student | POST `/quizzes/{id}/submit/` | student | Submit answers, get score |
| Document | POST `/documents/parse/` | teacher | Extract text from file |
| AI | POST `/ai/generate-quiz/` | teacher | Generate quiz via Gemini |
| Attempts | GET `/quizzes/{id}/attempts/` | teacher | Review submissions |

**Example — POST `/ai/generate-quiz/`:**
*Input:* `{ "topic": "Cells", "difficulty": "Medium", "question_count": 3 }`
*Output (201):* `{ "quiz": {...}, "questions": [ {...} x3 ] }`
*Errors:* `400` bad input/AI payload · `502` too few questions · `503` key missing.

Per-endpoint input/output detail: [API Design on GitHub](https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/docs/CSE4204-8D-T04_API-DESIGN.md).

---

## 8. AI Integration Workflow

**Why:** Writing MCQs by hand is slow; AI turns a topic + syllabus into
validated questions in seconds, with the teacher reviewing before use.

**Service:** Google Gemini (`gemini-2.5-flash`, default) or Anthropic Claude
(`claude-opus-4-8`), called server-side via the provider-agnostic
`backend/ai_integration/` package. The provider is chosen with `AI_PROVIDER` or a
per-request `provider` field. API keys (`GEMINI_API_KEY` / `ANTHROPIC_API_KEY`)
stay on the backend and are never exposed to the client.

```mermaid
flowchart LR
    A["Teacher input: topic, syllabus, difficulty, count"] --> B["Backend API - validation"]
    B --> C["Build structured prompt"]
    C --> D["Google Gemini API (generateContent)"]
    D --> E["Parse + validate JSON (4 options, correct A-D)"]
    E --> F["Save as Quiz + Question records"]
    F --> G["Frontend display / teacher review"]
```

**Validation before save:** non-empty title; non-empty questions list; every
question has 4 options, a prompt, an explanation; `correct_option ∈ {A,B,C,D}`;
returned count ≥ requested (else 502). If the key is missing or Gemini fails,
the API returns `503` with a clear message rather than crashing.

**How it improves the project:** faster quiz creation, consistent structure,
human-in-the-loop review, and safe server-side handling of the API key.

Full detail: [AI Integration Workflow on GitHub](https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/docs/CSE4204-8D-T04_AI-WORKFLOW.md).

---

## 9. References

- **GitHub Repository** — https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR
- Software Requirements Specification — https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/CSE4204-8D-T04_SRS.md
- Architecture Diagram — https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/diagrams/CSE4204-8D-T04_ARCHITECTURE-DIAGRAM.md
- ER Diagram — https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/diagrams/CSE4204-8D-T04_ER-DIAGRAM.md
- Use Case Diagram — https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/diagrams/CSE4204-8D-T04_USE_CASE_DIAGRAM.md
- Activity Diagrams — https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/diagrams/CSE4204-8D-T04_ACTIVITY-DIAGRAM.md
- API Design — https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/docs/CSE4204-8D-T04_API-DESIGN.md
- AI Integration Workflow — https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/docs/CSE4204-8D-T04_AI-WORKFLOW.md
- Django REST Framework — https://www.django-rest-framework.org/
- Google Gemini API — https://ai.google.dev/

---

*End of System Design Document — CSE4204-8D-T04 Smart Quiz Generator.*
