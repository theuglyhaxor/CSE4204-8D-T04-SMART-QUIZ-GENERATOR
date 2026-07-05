# Postman — Smart Quiz Generator API

**CSE4204-8D-T04 | Batch 8D | Team 04**

This folder contains a ready-to-run Postman collection and environment for
testing every backend API. Authentication is **JWT** (Bearer access tokens +
refresh tokens) via `djangorestframework-simplejwt`.

## Files

| File | Purpose |
|------|---------|
| `Smart_Quiz_Generator.postman_collection.json` | All API requests, grouped by area, with auto-token-capture test scripts. |
| `Smart_Quiz_Generator.postman_environment.json` | Environment variables (`baseUrl`, tokens, ids). |

## Setup

1. Open Postman → **Import** → select **both** JSON files in this folder.
2. Top-right environment selector → choose **Smart Quiz Generator - Local**.
3. Make sure the backend is running:
   ```bash
   cd backend
   python manage.py migrate
   python manage.py runserver        # serves http://127.0.0.1:8000
   ```
   > If you run on a different port (e.g. `runserver 8001`), update the
   > `baseUrl` environment variable to match.

## Recommended run order

The test scripts automatically save tokens and ids into environment variables,
so run requests roughly top to bottom:

1. **Auth → Register Teacher** → saves `teacherToken` (access) + `teacherRefresh`
2. **Auth → Register Student** → saves `studentToken` (access) + `studentRefresh`
3. **Quizzes → Create Quiz** → saves `quizId`
4. **Questions → Add Question to Quiz** → saves `questionId`
5. **Quiz Taking (Student) → Get Student-Safe Questions** (verify answers are hidden)
6. **Quiz Taking (Student) → Submit Quiz Attempt** (verify score)
7. **Attempts (Teacher) → List Attempts for Quiz**
8. **Documents & AI** (optional — AI needs an API key)
9. **Auth → Refresh Access Token** / **Auth → Logout** (JWT lifecycle)

> On a second run, registration will fail with **400 (duplicate username)**.
> Use **Auth → Login (Teacher)** instead to refresh the token, or change the
> usernames in the request bodies.

### JWT lifecycle requests

- **Refresh Access Token** — `POST /auth/token/refresh/` with `{"refresh": "{{teacherRefresh}}"}` returns a new access token (and saves it).
- **Logout** — `POST /auth/logout/` with `{"refresh": "{{teacherRefresh}}"}` blacklists the refresh token. After logout, **Refresh Access Token** returns **401**.

## What to verify (for the testing screenshots)

The assignment asks you to capture both success and failure paths. This
collection includes requests that demonstrate:

- ✅ **Successful responses** — register, login, create quiz, add question, submit.
- ❌ **Auth failure** — *Login (Wrong Password)* returns **401**.
- ❌ **Validation** — submitting an answer with a missing/invalid option returns **400**.
- 🔒 **Role enforcement** — *Create Quiz as Student* returns **403**; calling a
  protected route with no token returns **401**.
- 🙈 **Answer hiding** — *Get Student-Safe Questions* omits `correct_option`.
- 🔁 **JWT refresh & logout** — *Refresh Access Token* returns a new access token;
  after *Logout* the refresh token is blacklisted (subsequent refresh → 401).

## Alternative: scripted smoke test

A no-frontend, no-Postman end-to-end test also exists and exercises the same
flows automatically:

```bash
cd backend
python manage.py runserver
# in another terminal:
python manual_api_test.py
```
