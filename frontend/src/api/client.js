/**
 * Single place where the frontend talks to the Django API.
 *
 * - Base URL comes from VITE_API_BASE_URL (default "/api", which Vite proxies to the
 *   backend in dev — see vite.config.js — so there is no CORS round-trip locally).
 * - Sends the JWT access token as `Authorization: Bearer <token>`.
 * - On a 401, transparently refreshes the access token once and replays the request.
 *   Concurrent 401s share a single refresh instead of stampeding the endpoint.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

const ACCESS_KEY = "sqg_access";
const REFRESH_KEY = "sqg_refresh";
const USER_KEY = "sqg_user";

export const tokens = {
  access: () => localStorage.getItem(ACCESS_KEY),
  refresh: () => localStorage.getItem(REFRESH_KEY),
  user: () => {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY)) || null;
    } catch {
      return null;
    }
  },
  save: ({ access, refresh, user }) => {
    if (access) localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clear: () => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
  },
};

/** Error carrying the HTTP status, so callers can branch on 403 vs 503 etc. */
export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

/** Turn a DRF error body into one readable sentence. */
function messageFrom(data, status) {
  if (!data) return `Request failed (HTTP ${status})`;
  if (typeof data === "string") return data;
  if (data.detail) return data.detail;

  // DRF field errors: { username: ["already exists"], password: ["too short"] }
  const parts = Object.entries(data).map(([field, errors]) => {
    const text = Array.isArray(errors) ? errors.join(" ") : String(errors);
    return field === "non_field_errors" ? text : `${field}: ${text}`;
  });
  return parts.join(" · ") || `Request failed (HTTP ${status})`;
}

let refreshInFlight = null;

async function refreshAccessToken() {
  const refresh = tokens.refresh();
  if (!refresh) return null;

  // Collapse parallel refreshes into one in-flight request.
  if (!refreshInFlight) {
    refreshInFlight = fetch(`${BASE_URL}/auth/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!data?.access) return null;
        // ROTATE_REFRESH_TOKENS is on, so a new refresh comes back too.
        tokens.save({ access: data.access, refresh: data.refresh });
        return data.access;
      })
      .catch(() => null)
      .finally(() => {
        refreshInFlight = null;
      });
  }
  return refreshInFlight;
}

async function parse(response) {
  if (response.status === 204) return null;
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

async function send(path, { method = "GET", body, isForm = false, raw = false } = {}, retry = true) {
  const headers = {};
  const access = tokens.access();
  if (access) headers.Authorization = `Bearer ${access}`;
  if (body && !isForm) headers["Content-Type"] = "application/json";

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  });

  // Access token expired — refresh once, then replay the original request.
  if (response.status === 401 && retry && tokens.refresh()) {
    const fresh = await refreshAccessToken();
    if (fresh) return send(path, { method, body, isForm, raw }, false);

    // The refresh token is dead too: the session is over.
    tokens.clear();
    window.dispatchEvent(new Event("sqg:session-expired"));
  }

  if (!response.ok) {
    throw new ApiError(messageFrom(await parse(response), response.status), response.status);
  }

  return raw ? response.blob() : parse(response);
}

export const api = {
  get: (path) => send(path),
  post: (path, body) => send(path, { method: "POST", body }),
  patch: (path, body) => send(path, { method: "PATCH", body }),
  put: (path, body) => send(path, { method: "PUT", body }),
  delete: (path) => send(path, { method: "DELETE" }),

  /** multipart upload (document parsing) */
  upload: (path, file) => {
    const form = new FormData();
    form.append("file", file);
    return send(path, { method: "POST", body: form, isForm: true });
  },

  /** Fetch a PDF and hand back a Blob. */
  blob: (path) => send(path, { raw: true }),
};

/** Trigger a browser download for a quiz PDF. */
export async function downloadQuizPdf(quizId, { answers = true, filename } = {}) {
  const blob = await api.blob(`/quizzes/${quizId}/export-pdf/?answers=${answers}`);
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename || `quiz-${quizId}-${answers ? "answer-key" : "handout"}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

// --- Endpoint helpers ---------------------------------------------------------
export const auth = {
  login: (username, password) => api.post("/auth/login/", { username, password }),
  register: (payload) => api.post("/auth/register/", payload),
  me: () => api.get("/auth/me/"),
  logout: (refresh) => api.post("/auth/logout/", { refresh }),
};

export const quizzes = {
  list: () => api.get("/quizzes/"),
  get: (id) => api.get(`/quizzes/${id}/`),
  create: (payload) => api.post("/quizzes/", payload),
  update: (id, payload) => api.patch(`/quizzes/${id}/`, payload),
  remove: (id) => api.delete(`/quizzes/${id}/`),

  questions: (id) => api.get(`/quizzes/${id}/questions/`),
  addQuestion: (id, payload) => api.post(`/quizzes/${id}/questions/`, payload),
  studentQuestions: (id) => api.get(`/quizzes/${id}/student-questions/`),

  submit: (id, answers) => api.post(`/quizzes/${id}/submit/`, { answers }),
  attempts: (id) => api.get(`/quizzes/${id}/attempts/`),

  generate: (payload) => api.post("/ai/generate-quiz/", payload),
};

export const questions = {
  list: (quizId) => api.get(quizId ? `/questions/?quiz=${quizId}` : "/questions/"),
  update: (id, payload) => api.patch(`/questions/${id}/`, payload),
  remove: (id) => api.delete(`/questions/${id}/`),
};

export const attempts = {
  mine: () => api.get("/attempts/me/"),
};

export const meta = {
  team: () => api.get("/meta/"),
  stats: () => api.get("/stats/"),
};

export const documents = {
  parse: (file) => api.upload("/documents/parse/", file),
};
