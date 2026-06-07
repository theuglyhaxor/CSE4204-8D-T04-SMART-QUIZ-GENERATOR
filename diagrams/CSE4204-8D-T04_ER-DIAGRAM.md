# 2. ENTITY RELATIONSHIP DIAGRAM (ER DIAGRAM)
## CSE4204-8D-T04 Smart Quiz Generator

**Description:** The ER Diagram represents the database schema showing 7 entities and their relationships. It defines the data model for the Smart Quiz Generator, including users, quizzes, questions, student attempts, authentication tokens, and role management.

**Key Entities:**
- **User** - System users (teachers and students)
- **Group** - Role management (teacher/student groups)
- **AuthToken** - Token-based authentication
- **Quiz** - Quiz metadata and configuration
- **Question** - Quiz questions with options and answers
- **QuizAttempt** - Student submissions and scores

**Key Relationships:**
- 1 User can create many Quizzes (1:M)
- 1 Quiz contains many Questions (1:M)
- 1 Quiz has many QuizAttempts (1:M)
- 1 User has 1 AuthToken (1:1)
- 1 User belongs to 1 Group (1:1)

```mermaid
erDiagram
    USER ||--o{ GROUP : "belongs to"
    USER ||--o{ AUTHTOKEN : "has"
    USER ||--o{ QUIZ : "creates"
    QUIZ ||--o{ QUESTION : "contains"
    QUIZ ||--o{ QUIZATTEMPT : "has"
    QUESTION ||--o{ QUIZATTEMPT : "answered in"
    GROUP ||--o{ PERMISSION : "grants"

    USER {
        int user_id PK
        string email UK
        string password_hash
        string first_name
        string last_name
        datetime created_at
        datetime updated_at
        boolean is_active
    }

    GROUP {
        int group_id PK
        string name UK "teacher or student"
    }

    AUTHTOKEN {
        int token_id PK
        int user_id FK
        string token_hash UK
        datetime created_at
    }

    PERMISSION {
        int permission_id PK
        int group_id FK
        string action "create, read, update, delete"
    }

    QUIZ {
        int quiz_id PK
        int created_by FK "teacher user_id"
        string title
        text description
        string difficulty
        int duration_minutes
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    QUESTION {
        int question_id PK
        int quiz_id FK
        text prompt
        string option_a
        string option_b
        string option_c
        string option_d
        string correct_option "A, B, C, or D"
        text explanation
        int question_order
        datetime created_at
    }

    QUIZATTEMPT {
        int attempt_id PK
        int quiz_id FK
        string student_name
        json responses "student answers"
        int score
        int total "total questions"
        datetime created_at
    }
```

## Entity Details

| Entity | Purpose | Primary Key | Foreign Keys |
|--------|---------|-------------|--------------|
| **USER** | User accounts | user_id | - |
| **GROUP** | Role groups (teacher/student) | group_id | - |
| **AUTHTOKEN** | Authentication tokens | token_id | user_id |
| **PERMISSION** | Access permissions | permission_id | group_id |
| **QUIZ** | Quiz information | quiz_id | created_by (user_id) |
| **QUESTION** | Quiz questions | question_id | quiz_id |
| **QUIZATTEMPT** | Student submissions | attempt_id | quiz_id |

## Relationship Descriptions

### 1:1 Relationships
- **User ↔ AuthToken:** Each user has one authentication token
- **User ↔ Group:** Each user belongs to one role group

### 1:M Relationships
- **User → Quiz:** Teachers create multiple quizzes
- **Quiz → Question:** A quiz contains many questions
- **Quiz → QuizAttempt:** A quiz receives many student attempts
- **Group → Permission:** A group has many permissions

## Data Types

- **PK** = Primary Key (unique identifier)
- **FK** = Foreign Key (references another table)
- **UK** = Unique Key (must be unique)
- **int** = Integer
- **string** = Text (varchar)
- **text** = Long text (textarea)
- **json** = JSON data format
- **datetime** = Date and time
- **boolean** = True/False

---

**Related Files:**
- See [01-USE-CASE-DIAGRAM.md](01-USE-CASE-DIAGRAM.md) for functional requirements
- See [00-ARCHITECTURE-OVERVIEW.md](00-ARCHITECTURE-OVERVIEW.md) for system architecture
