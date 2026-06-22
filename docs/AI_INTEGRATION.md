# AI Integration

This package contains **all AI-related logic** for the Smart Quiz Generator,
deliberately isolated from the Django app (`quiz_api`). The web layer never talks
to an AI provider directly — it calls one function, `generate_quiz()`, and this
package decides which model to use and how.

The system supports **two interchangeable providers**:

| Provider | Model (default) | How it returns JSON | SDK |
|----------|-----------------|---------------------|-----|
| **Google Gemini** (default) | `gemini-2.5-flash` | Prompted for JSON; response parsed + fences stripped | None (stdlib `urllib`) |
| **Anthropic Claude** | `claude-opus-4-8` | Structured outputs (`output_config.format`) — schema-enforced JSON | `anthropic` |

Gemini is the default, so existing behaviour is unchanged. Claude is opt-in.

---

## 1. Why a separate package?

Originally the AI code lived in `quiz_api/services.py`, mixed in with the Django
app. It has now been extracted into this standalone package so that:

- **All AI logic lives in one place** — easy to find, review, and extend.
- **It is framework-independent** — none of these modules import Django models;
  they are plain Python and can be unit-tested or reused outside Django.
- **Adding a third provider** is a single new module + one line in `providers.py`.

> The folder is named `ai_integration` (not "AI integration") because a Python
> package must be a valid import identifier — it cannot contain spaces.

---

## 2. Module layout

```
ai_integration/
├── __init__.py        # public API — what the rest of the app imports
├── documents.py       # extract_text_from_uploaded_file()  (input pipeline)
├── prompts.py         # build_quiz_prompt()                 (provider-neutral prompt)
├── validation.py      # QUIZ_JSON_SCHEMA + validate_generated_quiz()  (the contract)
├── gemini.py          # generate_quiz_with_gemini()         (Google Gemini provider)
├── claude.py          # generate_quiz_with_claude()         (Anthropic Claude provider)
├── providers.py       # generate_quiz()                     (dispatcher)
├── generate_sample_quizzes_pdf.py   # CLI tool: generate quizzes -> PDF
└── README.md          # this document
```

### Responsibilities

- **`documents.py`** — turns an uploaded PDF/TXT/MD/CSV/JSON file into clean text.
  This is the *input* side of the AI pipeline (a teacher's source material).
- **`prompts.py`** — builds the generation prompt from the request fields
  (`topic`, `difficulty`, `syllabus`, `question_count`, `instruction`). The same
  prompt is used for every provider, so output is comparable across models.
- **`validation.py`** — the single source of truth for the quiz shape. It holds
  `QUIZ_JSON_SCHEMA` (which constrains Claude's structured output) and
  `validate_generated_quiz()` (the final gate every quiz passes through). Both
  providers converge here.
- **`gemini.py` / `claude.py`** — the two provider implementations. Each builds
  the prompt, calls its model, and returns the validated quiz.
- **`providers.py`** — `generate_quiz(payload, provider=None)` picks a provider
  and delegates.

---

## 3. The public API

Import everything you need from the package root:

```python
from ai_integration import generate_quiz, extract_text_from_uploaded_file

quiz = generate_quiz(request.data)                       # uses default provider
quiz = generate_quiz(request.data, provider="claude")    # force Claude
```

Full exported surface (see `__init__.py`):

`extract_text_from_uploaded_file`, `build_quiz_prompt` (+ alias
`build_gemini_prompt`), `QUIZ_JSON_SCHEMA`, `VALID_OPTIONS`, `strip_code_fences`,
`validate_generated_quiz`, `parse_gemini_response`, `generate_quiz_with_gemini`,
`generate_quiz_with_claude`, `generate_quiz`.

---

## 4. The quiz contract

Every provider must produce — and every quiz is validated against — this shape:

```json
{
  "title": "Quiz title",
  "questions": [
    {
      "prompt": "Question text",
      "option_a": "Option A",
      "option_b": "Option B",
      "option_c": "Option C",
      "option_d": "Option D",
      "correct_option": "A",
      "explanation": "Why A is correct"
    }
  ]
}
```

`validate_generated_quiz()` enforces:

- a non-empty `title`
- a non-empty `questions` list
- every question has a `prompt`, four non-empty options, and an `explanation`
- `correct_option` is one of `A`, `B`, `C`, `D` (normalised to uppercase)

Anything that fails raises a `ValueError`, which the API turns into an
HTTP 400. Provider/connectivity failures (no API key, network/HTTP errors)
raise `RuntimeError`, which the API turns into an HTTP 503.

---

## 5. Request → response flow

```
POST /api/ai/generate-quiz/        (teacher only)
        │
        ▼
GeminiGenerateQuizView (quiz_api/views.py)
        │  reads question_count, duration_minutes, difficulty, provider
        ▼
generate_quiz(payload, provider)   (ai_integration/providers.py)
        │
        ├── provider == "gemini" ──► generate_quiz_with_gemini()  (HTTP to Gemini)
        └── provider == "claude" ──► generate_quiz_with_claude()  (anthropic SDK)
        │
        ▼
validate_generated_quiz()          (shared gate)
        │
        ▼
Quiz + Question rows created, response returned (201)
```

---

## 6. Configuration

All keys are read from the environment (loaded from `backend/.env` by
`settings.py` via `python-dotenv`).

| Variable | Provider | Required? | Default |
|----------|----------|-----------|---------|
| `AI_PROVIDER` | dispatcher | optional | `gemini` |
| `GEMINI_API_KEY` | Gemini | required for Gemini | — |
| `GEMINI_MODEL` | Gemini | optional | `gemini-2.5-flash` |
| `GEMINI_TIMEOUT` | Gemini | optional | `30` (seconds) |
| `ANTHROPIC_API_KEY` | Claude | required for Claude | — |
| `CLAUDE_MODEL` | Claude | optional | `claude-opus-4-8` |

Example `backend/.env`:

```dotenv
# default provider for every request (optional; defaults to gemini)
AI_PROVIDER=gemini

# Gemini
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-2.5-flash

# Claude (only needed if you use the claude provider)
ANTHROPIC_API_KEY=your-anthropic-key
CLAUDE_MODEL=claude-opus-4-8
```

**Selecting the provider per request** — pass `"provider"` in the POST body
(this overrides `AI_PROVIDER`):

```json
{ "provider": "claude", "topic": "Photosynthesis", "question_count": 5, "difficulty": "Easy" }
```

If a provider's key is missing, that provider returns **HTTP 503** with a clear
message (`GEMINI_API_KEY is not configured.` / `ANTHROPIC_API_KEY is not
configured.`) — the rest of the app keeps working.

---

## 7. Sample-quiz PDF tool

`generate_sample_quizzes_pdf.py` generates real quizzes via this package and
renders them to PDFs (questions, options with the correct answer highlighted,
explanations, and an answer-key page) so you can eyeball quality without a
frontend. Nothing is written to the database.

```bash
cd backend

# default topics, default provider (gemini)
python ai_integration/generate_sample_quizzes_pdf.py

# your own topics
python ai_integration/generate_sample_quizzes_pdf.py "Python basics" "World War II"

# use Claude instead
python ai_integration/generate_sample_quizzes_pdf.py --provider claude "Quantum physics"
```

PDFs are written to `backend/sample_quizzes/`. The tool retries transient
rate-limit (429) and overload (503) errors with backoff. Requires `fpdf2`.

---

## 8. Adding a new provider

1. Create `ai_integration/newprovider.py` with a
   `generate_quiz_with_newprovider(payload)` function that builds the prompt with
   `build_quiz_prompt`, calls the model, and returns `validate_generated_quiz(...)`.
2. Add a branch for it in `providers.py`.
3. Export it from `__init__.py` if callers need it directly.

The shared prompt + validation mean a new provider is only the model call.
