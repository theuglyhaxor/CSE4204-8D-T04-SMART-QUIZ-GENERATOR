# Frontend Developer Guide

The frontend **lives in this repository**, at [`frontend/`](../frontend/). It is a React 18 + Vite 5
single-page app that talks to the Django REST backend.

This guide explains how it is put together and how to extend it.

---

## Running it

```bash
# terminal 1 — backend
cd backend
python manage.py migrate
python manage.py runserver          # http://127.0.0.1:8000

# terminal 2 — frontend
cd frontend
npm install
npm run dev                         # http://127.0.0.1:5173
```

### Why there is no CORS problem in development

[`vite.config.js`](../frontend/vite.config.js) proxies `/api` → `http://127.0.0.1:8000`:

```js
server: {
  proxy: { '/api': { target: BACKEND, changeOrigin: true } },
}
```

The browser therefore only ever sees **one origin** (`:5173`), so cross-origin rules never apply.
`CORS_ALLOWED_ORIGINS` in the backend only matters when you serve the frontend from a *different*
origin (e.g. a production deployment).

### Configuration

| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | `/api` | Where API calls go. Keep the default in dev. Set a full URL (`https://api.example.com/api`) when the backend is deployed elsewhere. |
| `VITE_BACKEND_URL` | `http://127.0.0.1:8000` | Where the dev proxy forwards `/api`. |

See [`frontend/.env.example`](../frontend/.env.example).

---

## Architecture

```
src/
├── api/client.js            # the ONLY place that calls the backend
├── context/AuthContext.jsx  # session state (user, signIn, signUp, signOut)
├── components/
│   ├── ProtectedRoute.jsx   # auth + role gate for a route
│   ├── TeamFooter.jsx       # identity footer, fed by GET /api/meta/
│   └── …                    # Sidebar, Navbar, QuizTable, QuizConfig, modals…
├── pages/
│   ├── Login.jsx  Register.jsx                           # public
│   ├── Dashboard.jsx  CreateQuiz.jsx  QuestionBank.jsx   # teacher
│   ├── StudentHome.jsx  TakeQuiz.jsx  MyAttempts.jsx     # student
│   └── UserProfile.jsx  Settings.jsx                     # any signed-in user
├── App.jsx                  # routing + role redirects
└── styles.css               # design tokens + shared primitives
```

### Rule: all network access goes through `api/client.js`

Never call `fetch` from a component. The client owns token handling, and bypassing it means bypassing
automatic refresh.

```js
import { quizzes, attempts, meta, downloadQuizPdf } from "../api/client";

const list      = await quizzes.list();
const generated = await quizzes.generate({ topic: "Photosynthesis", question_count: 5 });
const result    = await quizzes.submit(quizId, [{ question: 1, selected_option: "B" }]);
const mine      = await attempts.mine();
const stats     = await meta.stats();

await downloadQuizPdf(quizId, { answers: false });   // triggers a browser download
```

---

## Authentication

The backend issues a JWT **access** token (60 min) and a **refresh** token (1 day, rotating).

### What the client does for you

1. Attaches `Authorization: Bearer <access>` to every request.
2. On a **401**, transparently calls `/auth/token/refresh/`, stores the new pair, and **replays the
   original request**. Concurrent 401s share a single refresh rather than stampeding the endpoint.
3. If the refresh *also* fails, it clears storage and fires a `sqg:session-expired` event, which
   `AuthContext` listens for to drop the session.

A component therefore never has to think about token expiry.

### Session state

```jsx
import { useAuth } from "../context/AuthContext";

const { user, loading, isAuthenticated, isTeacher, isStudent, signIn, signUp, signOut } = useAuth();
// user = { id, username, email, role }
```

On boot, `AuthContext` calls `GET /auth/me/` to confirm a stored token is still valid, so a stale or
blacklisted token doesn't render the app as if it were logged in. `loading` is `true` while that check
is in flight — `ProtectedRoute` waits on it instead of bouncing to `/login` and back.

### Guarding a route

```jsx
<Route
  path="/create-quiz"
  element={
    <ProtectedRoute role="teacher">
      <CreateQuiz />
    </ProtectedRoute>
  }
/>
```

Omit `role` to allow any signed-in user. A signed-in user with the *wrong* role is redirected to their
own home rather than a dead end.

> **Route guards are convenience, not security.** Every rule is enforced server-side. The guards only
> avoid showing a user a screen that would fail anyway.

---

## Error handling

`api/client.js` throws an `ApiError` carrying `.status` and a human-readable `.message`, flattening
DRF's field errors (`{"username": ["already exists"]}` → `username: already exists`).

```jsx
try {
  await quizzes.generate(config);
} catch (err) {
  if (err.status === 503) {
    setError("AI is not configured on the server. Add an API key to backend/.env.");
  } else {
    setError(err.message);
  }
}
```

Statuses worth branching on:

| Status | Meaning |
|---|---|
| `400` | Validation failed |
| `401` | Not signed in (the client already tried to refresh) |
| `403` | Signed in, but wrong role — or not the quiz's owner |
| `404` | No such quiz/question |
| `502` | The AI provider returned fewer questions than requested |
| `503` | AI provider key not configured |

---

## Key flows

### Teacher — generate a quiz

1. `QuizConfig` collects topic, difficulty, count, duration, provider, and an optional source document.
2. If a file was attached, `CreateQuiz` first calls `documents.parse(file)` and feeds the extracted text
   in as `syllabus`.
3. `quizzes.generate(payload)` → the backend calls the model, validates the JSON, and **saves the quiz
   as a draft**, returning `{ quiz, questions }`.
4. `QuizPreview` renders them for review. The teacher then **publishes**
   (`quizzes.update(id, { is_active: true })`), exports a PDF, or discards (deletes) it.

New quizzes are **drafts** — invisible to students until published.

### Student — take a quiz

1. `quizzes.studentQuestions(id)` returns the questions **without** `correct_option` or `explanation`.
   The answer key is never in the browser before submitting.
2. `TakeQuiz` runs a countdown; at zero it auto-submits whatever has been answered.
3. `quizzes.submit(id, answers)` scores server-side and returns the score *plus* the correct answers and
   explanations, which the result screen uses to render the review.

---

## Team identity footer

`TeamFooter` reads `GET /api/meta/`, which is backed by the `TEAM` dict in
[`backend/smart_quiz_backend/settings.py`](../backend/smart_quiz_backend/settings.py) — the **same**
source the exported PDF footer uses. Edit the team in that one place and both the app and the PDFs
update. Never hardcode member names in a component.

```jsx
<TeamFooter />          {/* full block: members, course, university */}
<TeamFooter compact />  {/* one line, used on the auth screens */}
```

---

## Styling

- Design tokens (`--sqg-primary`, `--sqg-muted`, `--sqg-border`, …) and shared primitives
  (`.btn`, `.banner`, `.badge-pill`, `.spinner`, `.state-block`, `.modal`) live in `src/styles.css`.
- Per-component CSS sits next to the component.
- Dark mode is a `body.dark` class toggled in `App.jsx` and persisted to `localStorage`.

**Gotcha:** anything shared across pages must live in `styles.css`, not in a single component's CSS
file. A page only loads the CSS of the components it actually imports — which is why the student pages
explicitly `import "./Dashboard.css"`: they reuse its `.dashboard` shell layout but never render
`Dashboard` itself.

---

## Building for production

```bash
cd frontend
npm run build          # → frontend/dist/
npm run preview        # serve the build locally
```

Serve `dist/` as static files and set `VITE_API_BASE_URL` to the deployed API's URL. Add that origin to
the backend's `CORS_ALLOWED_ORIGINS`, since the Vite proxy is no longer sitting in front of it.
