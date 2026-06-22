# 4. ACTIVITY DIAGRAMS
## CSE4204-8D-T04 Smart Quiz Generator

**Description:** Activity diagrams describe the step-by-step workflow of major features, showing user actions, system processes, decision points, and outputs. This document covers the four most important workflows of the Smart Quiz Generator:

1. **AI Question Generation** (primary/major feature)
2. **Student Takes & Submits a Quiz**
3. **User Registration & Login**
4. **Document Upload & Parsing**

Each diagram is drawn as a Mermaid flowchart where diamonds (`{ }`) are **decision points** and rectangles are **actions/processes**.

> **Legend:** 🟦 User action · ⚙️ System/backend process · ☁️ External AI service · 🔶 Decision point

---

## 4.1 AI Question Generation Workflow (Major Feature)

This is the flagship workflow. A teacher requests AI-generated questions; the backend builds a prompt, calls Google Gemini, validates the response, persists a `Quiz` + `Question` records, and returns them.

Backed by [`GeminiGenerateQuizView`](../backend/quiz_api/views.py) and the AI package [`generate_quiz()`](../backend/ai_integration/providers.py) (Gemini/Claude dispatcher).

```mermaid
flowchart TD
    Start(["Teacher requests AI quiz generation"]) --> Auth{"Authenticated teacher?"}
    Auth -- No --> Rej["Return 401 / 403"]:::err
    Auth -- Yes --> Input["POST /api/ai/generate-quiz/ (title, topic, syllabus, difficulty, question_count)"]:::user

    Input --> Valid{"Valid input? question_count >= 1, integers ok"}
    Valid -- No --> Err400["Return 400 - validation error"]:::err
    Valid -- Yes --> Key{"GEMINI_API_KEY configured?"}

    Key -- No --> Err503["Return 503 - Service Unavailable"]:::err
    Key -- Yes --> Prompt["Build structured prompt (build_gemini_prompt)"]:::sys
    Prompt --> Call["Call Google Gemini API (generateContent)"]:::ai

    Call --> Net{"API call succeeded?"}
    Net -- No --> Err503b["Return 503 - Gemini request failed"]:::err
    Net -- Yes --> Parse["Parse and validate JSON (validate_generated_quiz)"]:::sys

    Parse --> Shape{"Valid shape? 4 options, correct A-D, title present"}
    Shape -- No --> Err400b["Return 400 - invalid AI payload"]:::err
    Shape -- Yes --> CountChk{"Returned count >= requested count?"}
    CountChk -- No --> Err502["Return 502 - Bad Gateway"]:::err

    CountChk -- Yes --> Save["Create Quiz record + linked Question records"]:::sys
    Save --> Resp["Return 201 - quiz and questions"]:::sys
    Resp --> Review["Teacher reviews generated questions"]:::user
    Review --> Done(["End"])

    classDef user fill:#e1f5ff,stroke:#0288d1
    classDef sys fill:#f3e5f5,stroke:#8e24aa
    classDef ai fill:#fce4ec,stroke:#d81b60
    classDef err fill:#ffebee,stroke:#c62828
```

**Key decision points:** authentication/role check, input validation, API-key presence, network success, AI payload shape validation, requested-count check.

---

## 4.2 Student Takes & Submits a Quiz

The student fetches answer-free questions, answers them, and submits. The backend scores the attempt server-side and stores it.

Backed by [`QuizStudentQuestionsView`](../backend/quiz_api/views.py) and [`QuizSubmitView`](../backend/quiz_api/views.py).

```mermaid
flowchart TD
    Start(["Student logs in"]) --> List["GET /api/quizzes/ - view active quizzes"]:::user
    List --> Pick["Select a quiz"]:::user
    Pick --> Fetch["GET /api/quizzes/{id}/student-questions/"]:::user
    Fetch --> Safe["System returns questions WITHOUT correct_option"]:::sys

    Safe --> Answer["Student answers each question"]:::user
    Answer --> Submit["POST /api/quizzes/{id}/submit/ - answers list + student_name"]:::user

    Submit --> ChkList{"answers is a non-empty list?"}
    ChkList -- No --> Err["Return 400"]:::err
    ChkList -- Yes --> Loop["For each answer: validate question id and selected_option"]:::sys

    Loop --> Belongs{"Question belongs to this quiz?"}
    Belongs -- No --> Err
    Belongs -- Yes --> Compare{"selected_option equals correct_option?"}
    Compare -- Yes --> Inc["score = score + 1"]:::sys
    Compare -- No --> Skip["record incorrect"]:::sys
    Inc --> More{"More answers?"}
    Skip --> More
    More -- Yes --> Loop
    More -- No --> Store["Create QuizAttempt (score, total, responses JSON)"]:::sys

    Store --> Result["Return 201 - score, total, percentage, per-question result"]:::sys
    Result --> View["Student views score and feedback"]:::user
    View --> Done(["End"])

    classDef user fill:#e1f5ff,stroke:#0288d1
    classDef sys fill:#f3e5f5,stroke:#8e24aa
    classDef err fill:#ffebee,stroke:#c62828
```

**Note:** Scoring is always performed on the server using the stored `correct_option`; the student-facing endpoint never exposes correct answers, preventing client-side cheating.

---

## 4.3 User Registration & Login

Registration creates a Django user, assigns a role group (`teacher`/`student`), and issues a DRF token. Login authenticates credentials and returns the token.

Backed by [`AuthRegisterView`](../backend/quiz_api/views.py) and [`AuthLoginView`](../backend/quiz_api/views.py).

```mermaid
flowchart TD
    Start(["User opens app"]) --> Choice{"New user?"}

    Choice -- Yes --> Reg["POST /api/auth/register/ - username, password, role"]:::user
    Reg --> Uniq{"Username available?"}
    Uniq -- No --> RegErr["Return 400 - username exists"]:::err
    Uniq -- Yes --> Create["Create user + add to role group + issue token"]:::sys
    Create --> Token["Return 201 - token and user role"]:::sys

    Choice -- No --> Login["POST /api/auth/login/ - username, password"]:::user
    Login --> AuthChk{"Credentials valid?"}
    AuthChk -- No --> LoginErr["Return 401 - invalid credentials"]:::err
    AuthChk -- Yes --> GetToken["Get or create token"]:::sys
    GetToken --> Token

    Token --> Use["Client stores token, sends Authorization header"]:::user
    Use --> Done(["End"])

    classDef user fill:#e1f5ff,stroke:#0288d1
    classDef sys fill:#f3e5f5,stroke:#8e24aa
    classDef err fill:#ffebee,stroke:#c62828
```

---

## 4.4 Document Upload & Parsing

A teacher uploads a learning document; the backend extracts text based on file type. (Document parsing and AI generation are currently separate endpoints — see [AI Integration Workflow](../docs/CSE4204-8D-T04_AI-WORKFLOW.md).)

Backed by [`DocumentParseView`](../backend/quiz_api/views.py) and [`extract_text_from_uploaded_file()`](../backend/ai_integration/documents.py).

```mermaid
flowchart TD
    Start(["Teacher uploads file"]) --> Post["POST /api/documents/parse/ - multipart file field"]:::user
    Post --> Has{"File provided?"}
    Has -- No --> Err1["Return 400 - no file"]:::err
    Has -- Yes --> Type{"Supported type? pdf, txt, md, csv, json"}

    Type -- No --> Err2["Return 400 - unsupported type"]:::err
    Type -- Yes --> Branch{"Is PDF?"}
    Branch -- Yes --> Pdf["Extract text via pypdf, per page"]:::sys
    Branch -- No --> Txt["Decode UTF-8 text"]:::sys

    Pdf --> Clean["Clean and trim text"]:::sys
    Txt --> Clean
    Clean --> Empty{"Readable text found?"}
    Empty -- No --> Err3["Return 400 - empty document"]:::err
    Empty -- Yes --> Out["Return text, filename, page_count, word_count"]:::sys
    Out --> Done(["End"])

    classDef user fill:#e1f5ff,stroke:#0288d1
    classDef sys fill:#f3e5f5,stroke:#8e24aa
    classDef err fill:#ffebee,stroke:#c62828
```

---

## Implementation vs. Planned

| Workflow | Status | Note |
|----------|--------|------|
| AI question generation | ✅ Implemented | Generation takes `topic`/`syllabus` text input directly. |
| Student take & submit | ✅ Implemented | Server-side scoring; responses stored as JSON. |
| Registration & login | ✅ Implemented | Username-based; role via Django Group. |
| Document parsing | ✅ Implemented | Parsing endpoint returns text only. |
| Parse → AI in one step | 🟡 Planned | SRS UC-2 describes uploading a document that directly feeds AI generation; currently parse and generate are two endpoints. |
| Logout / token invalidation | 🟡 Planned (FR-06) | No `/auth/logout/` route implemented yet. |

---

**Repository:** https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR

**Related Files (GitHub):**
- [Use Case Diagram](https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/diagrams/CSE4204-8D-T04_USE_CASE_DIAGRAM.md)
- [ER Diagram](https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/diagrams/CSE4204-8D-T04_ER-DIAGRAM.md)
- [Architecture Diagram](https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/diagrams/CSE4204-8D-T04_ARCHITECTURE-DIAGRAM.md)
- [AI Integration Workflow](https://github.com/theuglyhaxor/CSE4204-8D-T04-SMART-QUIZ-GENERATOR/blob/main/docs/CSE4204-8D-T04_AI-WORKFLOW.md)
