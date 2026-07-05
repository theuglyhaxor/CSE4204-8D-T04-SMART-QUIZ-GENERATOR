# Development Roadmap

**Project:** SMART QUIZ GENERATOR
**Course Code:** CSE4204-8D-T04 | **Batch:** 8D | **Team:** 04

This roadmap defines the development plan for the remaining weeks of the semester. It outlines the major modules, the sequence in which they are built, the responsibilities assigned to each team member, and the expected completion timeline.

---

## 1. Team Responsibilities Overview

| No. | Name | Student ID | Primary Responsibility |
|---|---|---|---|
| 1 | MD Rohan | 11220320958 | Backend Developer, Full Stack Development |
| 2 | Sharmin Nahar Tumpa | 11220320962 | AI Integration |
| 3 | Pial Tarofdar | 11220320965 | Frontend Developer |
| 4 | Sanjana Athoy | 11220320953 | Overall Technical Help, QA & Testing |

---

## 2. Major Modules

| Module | Description | Lead |
|---|---|---|
| **Authentication & Authorization** | Token-based auth, role-based access control (Teacher / Student) | MD Rohan |
| **Quiz Management (Backend)** | CRUD for quizzes, questions, options, attempts via Django REST API | MD Rohan |
| **AI Question Generation** | Document parsing (PDF, TXT, MD, CSV, JSON) + Gemini-powered question generation | Sharmin Nahar Tumpa |
| **Frontend Application** | Teacher and Student dashboards, quiz-taking UI, results views | Pial Tarofdar |
| **Scoring & Reporting** | Real-time scoring, attempt history, performance analytics | MD Rohan / Sharmin |
| **Testing & QA** | Unit tests, integration tests, bug tracking, validation | Sanjana Athoy |
| **Deployment** | Docker, Gunicorn, Nginx, environment configuration | MD Rohan |

---

## 3. Development Sequence

The project follows an API-first, incremental delivery approach:

1. **Backend foundation** — models, REST endpoints, and authentication are completed first so every other module has a stable contract to build against.
2. **Frontend layer** — built on top of the finalized API, consuming endpoints for both Teacher and Student roles.
3. **AI integration** — connected through the backend service layer and surfaced in the frontend.
4. **Feature completion** — remaining features wired end-to-end and polished.
5. **Testing & debugging** — full-system validation across all modules.
6. **Deployment** — containerized release to a hosting environment.

---

## 4. Weekly Plan & Expected Timeline

### Week 06 — Backend Development
- Finalize Django models (Quiz, Question, QuizAttempt) and migrations.
- Complete REST API endpoints and DRF serializers.
- Implement token-based authentication and role-based permissions.
- Seed sample data and verify endpoints via API testing.
- **Owner:** MD Rohan
- **Deliverable:** Stable, documented backend API.

### Week 07 — Frontend Development
- Set up frontend project (React / Vue) and routing.
- Build login/registration and role-based dashboards.
- Implement quiz listing, quiz-taking, and submission screens.
- Integrate frontend with backend API endpoints.
- **Owner:** Pial Tarofdar (support: MD Rohan)
- **Deliverable:** Working frontend connected to the live API.

### Week 08 — AI Integration
- Integrate Google Gemini API through the backend service layer.
- Implement document parsing for PDF, TXT, MD, CSV, and JSON.
- Expose AI question-generation endpoint and wire it into the frontend.
- Validate generated question quality and formatting.
- **Owner:** Sharmin Nahar Tumpa (support: MD Rohan)
- **Deliverable:** End-to-end AI-powered question generation.

### Week 09 — Feature Completion
- Implement real-time scoring and result calculation.
- Add attempt history and performance analytics for teachers.
- Complete quiz activation/deactivation and answer explanations.
- Polish UI/UX and handle edge cases.
- **Owner:** Full team
- **Deliverable:** Feature-complete application.

### Week 10 — Testing and Debugging
- Write and run unit and integration tests.
- Perform end-to-end testing of all user workflows.
- Fix bugs, validate security and access control.
- Conduct user acceptance testing.
- **Owner:** Sanjana Athoy (support: full team)
- **Deliverable:** Verified, stable build.

### Week 11 — Deployment
- Containerize the application with Docker.
- Configure Gunicorn + Nginx and production settings.
- Deploy to hosting environment and run smoke tests.
- Finalize documentation and prepare project demonstration.
- **Owner:** MD Rohan (support: full team)
- **Deliverable:** Deployed, presentable production application.

---

## 5. Timeline Summary

| Week | Phase | Lead | Status |
|---|---|---|---|
| Week 06 | Backend Development | MD Rohan | ✅ Completed |
| Week 07 | Frontend Development | Pial Tarofdar | 🔄 In Progress |
| Week 08 | AI Integration | Sharmin Nahar Tumpa | ✅ Completed |
| Week 09 | Feature Completion | Full Team | ⏳ Planned |
| Week 10 | Testing and Debugging | Sanjana Athoy | ⏳ Planned |
| Week 11 | Deployment | MD Rohan | ⏳ Planned |


---

*Document prepared for CSE4204-8D-T04 — Smart Quiz Generator.*
