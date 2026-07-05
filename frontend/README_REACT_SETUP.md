# Frontend (React) Setup - SMART QUIZ GENERATOR

This folder contains a separate React frontend that calls the Django backend APIs.

## Tech
- React + Vite
- Fetch API

## Run (from this repo root)
```bash
cd frontend
npm install
npm run dev
```

Frontend dev server will run at:
- http://127.0.0.1:5173

## Backend API base
Edit `src/api/client.js`:
- `API_BASE_URL` default: `http://127.0.0.1:8001/api`

## Token header
Backend protected endpoints expect:
- `Authorization: Token <access_token>`

This starter stores token in:
- `localStorage.setItem('quiz_token', accessToken)`

## Note about CORS
Add your frontend origin in backend env var `CORS_ALLOWED_ORIGINS`, e.g.:
- `http://127.0.0.1:5173`

