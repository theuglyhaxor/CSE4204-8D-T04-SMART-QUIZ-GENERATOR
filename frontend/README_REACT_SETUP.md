# Frontend (React) — SMART QUIZ GENERATOR

The React + Vite single-page app for the Smart Quiz Generator. It talks to the Django backend in
[`../backend/`](../backend/).

Full guide: **[docs/FRONTEND_DEVELOPER_GUIDE.md](../docs/FRONTEND_DEVELOPER_GUIDE.md)**

## Tech

- React 18 + Vite 5
- React Router 7
- lucide-react (icons)
- Fetch API (no axios)

## Run

Start the backend first:

```bash
cd ../backend
python manage.py migrate
python manage.py runserver          # http://127.0.0.1:8000
```

Then, in a second terminal:

```bash
cd frontend
npm install
npm run dev                         # http://127.0.0.1:5173
```

Open http://127.0.0.1:5173 and sign up as a **Teacher** or a **Student**.

## Backend API base

Configured with `VITE_API_BASE_URL`, default **`/api`**. See [`.env.example`](.env.example).

Do not hardcode a base URL in a component — all API access goes through
[`src/api/client.js`](src/api/client.js).

## Auth header

Protected endpoints use **JWT**:

```
Authorization: Bearer <access_token>
```

`src/api/client.js` attaches this automatically, and transparently refreshes the access token and
replays the request on a 401. Tokens are stored under `sqg_access` / `sqg_refresh` / `sqg_user`.

## CORS

**Not an issue in development.** `vite.config.js` proxies `/api` → `http://127.0.0.1:8000`, so the
browser only ever sees one origin.

You only need to add an origin to the backend's `CORS_ALLOWED_ORIGINS` when you serve the built app
from a *different* origin (i.e. in production).

## Build

```bash
npm run build      # -> dist/
npm run preview
```
