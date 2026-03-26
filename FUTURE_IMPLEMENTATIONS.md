# 🚀 Future Implementations & Improvement Plan
### psycho_one — Psychometric Assessment Platform
> Last updated: 2026-03-26

---

## Table of Contents

1. [Scoring & Results Engine](#1-scoring--results-engine)
2. [Assessment Modules](#2-assessment-modules)
3. [Report System](#3-report-system)
4. [User Management & Authentication](#4-user-management--authentication)
5. [Frontend & UX Improvements](#5-frontend--ux-improvements)
6. [Backend & API Improvements](#6-backend--api-improvements)
7. [Database & Infrastructure](#7-database--infrastructure)
8. [Admin & Analytics Dashboard](#8-admin--analytics-dashboard)
9. [AI / ML Integrations](#9-ai--ml-integrations)
10. [Deployment & DevOps](#10-deployment--devops)

---

## 1. Scoring & Results Engine

### 🔴 High Priority (Known Gaps)

- **Enneagram Scoring Logic**
  - Questions are seeded but scoring is unimplemented.
  - Implement wing calculation (e.g., Type 5w6 vs. 5w4) and tritype logic.
  - Files to create: `backend/scoring_enneagram.py`

- **Brain Dominance Scoring**
  - Left/Right Brain Dominance questions exist in `left_right_brain.txt`.
  - Implement weighted scoring: calculate Left% vs. Right% dominance percentage.
  - Files to create: `backend/scoring_brain_dominance.py`

- **Real MBTI Cognitive Functions**
  - The 4 cognitive functions (Dominant, Auxiliary, Tertiary, Inferior) are currently mocked.
  - Replace with real derivation based on the MBTI 4-letter type result.
  - Update: `backend/scoring_mbti.py` → add `get_cognitive_functions(mbti_type)`.

- **Real Quiz Duration Tracking**
  - Session `duration_seconds` is currently hardcoded as `1200`.
  - Record actual `started_at` from the frontend and compute `completed_at - started_at` on the backend.

### 🟡 Medium Priority

- **Multiple Intelligence Scoring**
  - Questions exist in `multiple_intelligence_questions.txt` but are not seeded.
  - Implement scoring across Howard Gardner's 8 intelligence types.
  - Files to create: `backend/seed_multiple_intelligence.py`, `backend/scoring_multiple_intelligence.py`

- **Composite / Cross-Subtest Insights**
  - Currently, `composite_insights` in the report are generic.
  - Use the results of 2+ subtests to generate cross-referenced career and personality insights.
  - Example: Correlate MBTI `INTJ` with `Enneagram Type 5` to suggest specific career paths.

---

## 2. Assessment Modules

### 🟡 Medium Priority

- **Big Five (OCEAN) Personality Model**
  - A highly validated and globally recognized framework (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism).
  - Add seed script, scoring logic, and report section.
  - The `Question.category` field is already designed with `big_five` as a likely value.

- **Multiple Intelligences Module**
  - Fully integrate the questions from `multiple_intelligence_questions.txt`.
  - Display radar/spider chart on the report for the 8 intelligence types.

- **Aptitude / Cognitive Ability Tests**
  - Add numerical reasoning, verbal reasoning, and abstract pattern questions.
  - Scoring would use `correct_answer` field (already in the `Question` model).

- **Values & Motivation Assessment**
  - A shorter questionnaire on what drives a candidate (e.g., autonomy, security, growth).

### 🟢 Low Priority

- **DISC Assessment**
  - Dominance, Influence, Steadiness, Conscientiousness — commonly used in hiring.

- **Emotional Intelligence (EQ) Assessment**
  - Measure self-awareness, empathy, and emotional regulation.

---

## 3. Report System

### 🔴 High Priority

- **Wire Up Live Report (`report.html`) to Real Data**
  - `report.html` is the live report template but is not yet fully connected to the backend JSON structure from `GET /api/report/{id}`.
  - Audit the template and ensure all sections (charts, text, scores) render from the API response.

- **Temperament Results in Report**
  - Temperament scoring is implemented and returned in `/submit-exam`, but `temperament_type` and `temperament_description` are not yet saved to `report_data` JSON and not displayed in the report.
  - Add Temperament as a subtest block inside `report_data["subtests"]`.

### 🟡 Medium Priority

- **PDF Export**
  - Allow candidates to download their report as a PDF.
  - Options: use `WeasyPrint` or `Puppeteer` (headless Chrome) to render `report.html` to PDF server-side.
  - Add endpoint: `GET /api/report/{id}/pdf`

- **Shareable Report Link**
  - Generate a unique, time-limited URL for each report so candidates can share it.
  - Consider adding a `share_token` and `expires_at` field to the `Report` model.

- **Report Versioning**
  - If a candidate retakes an assessment, store multiple report versions and allow comparison.

### 🟢 Low Priority

- **Email Report Delivery**
  - After submission, automatically email the report PDF to the candidate.
  - Use `FastMail` or `SendGrid` with a Jinja2 HTML email template.

---

## 4. User Management & Authentication

### 🔴 High Priority

- **Admin Authentication**
  - Add a simple token-based or session-based login for administrators who view candidate data.
  - Protect all `/api/` routes with auth middleware.

### 🟡 Medium Priority

- **Candidate Profile Page**
  - Allow returning candidates to look up their past reports using their email.
  - Add endpoint: `GET /api/user/{email}/reports`

- **Country Field for User**
  - The pre-exam registration form collects `country`, but the `User` model only stores `name`, `email`, and `education`.
  - Add `country = Column(String(100), nullable=True)` to `models.User` and create an Alembic migration.

- **Role-Based Access**
  - Roles: `Candidate`, `Assessor`, `Admin`
  - Assessors can view candidate reports; Admins can manage questions and users.

### 🟢 Low Priority

- **OAuth / Social Login**
  - Allow candidates to sign in using Google or LinkedIn for a smoother pre-exam experience.

---

## 5. Frontend & UX Improvements

### 🔴 High Priority

- **Session Resume / Progress Save**
  - If a candidate closes the browser during the exam, their progress is lost on the frontend.
  - Save answers to `localStorage` as the user progresses; reload on re-entry.

- **Question Navigation**
  - Add a question map/grid (like an OMR sheet) showing answered vs. unanswered questions.
  - Allow candidates to jump to any question and review before submitting.

- **Loading & Transition States**
  - Show a proper loading spinner when fetching questions and submitting the exam.
  - Add a transition animation between assessment modules.

### 🟡 Medium Priority

- **Timer per Section**
  - Display a countdown timer per assessment module (e.g., 20 min for MBTI, 15 min for Temperament).
  - Auto-submit when time runs out.

- **Animated Results Reveal**
  - On the report page, animate the score bars and type reveal for a more engaging experience.

- **Mobile Responsiveness**
  - Audit `session.html` and `report.html` on small screen sizes.
  - Ensure the question layout and option buttons are touch-friendly.

- **Dark Mode Toggle**
  - Add a persistent dark/light mode preference stored in `localStorage`.

### 🟢 Low Priority

- **Multilingual Support (i18n)**
  - Allow the UI and questions to be served in multiple languages.
  - Use a JSON-based translation file per language.

---

## 6. Backend & API Improvements

### 🔴 High Priority

- **Input Validation on `/submit-exam`**
  - Validate that all required questions were answered before accepting submission.
  - Return a `400` error with which categories are incomplete.

- **Prevent Duplicate Submissions**
  - A user with the same email should not be able to submit a second session if one is already `in_progress`.

### 🟡 Medium Priority

- **Paginated Question API**
  - `GET /questions` currently returns all questions at once.
  - Add `?limit=50&offset=0` pagination or return questions grouped by category.

- **Background Task for Report Generation**
  - Use FastAPI's `BackgroundTasks` so the report is generated asynchronously, improving the response time of `/submit-exam`.

- **Response Time Tracking**
  - Store `answered_at` per `Response` (already available in the model).
  - Analyze time-per-question to flag rushed or skipped sections.

### 🟢 Low Priority

- **Webhook / Event System**
  - Fire events (e.g., `exam.completed`, `report.generated`) so the platform can integrate with external HR tools.

- **Rate Limiting**
  - Protect public endpoints (`/session`, `/submit-exam`) against abuse using `slowapi`.

---

## 7. Database & Infrastructure

### 🔴 High Priority

- **Add `country` to `User` Model**
  - Already collected via form; needs an Alembic migration to persist it.
  ```bash
  alembic revision --autogenerate -m "add country to users"
  alembic upgrade head
  ```

- **Index Optimization**
  - Add a composite index on `(session_id, question_id)` in `Responses` for faster scoring queries.

### 🟡 Medium Priority

- **Soft Delete for Users & Sessions**
  - Add `is_deleted = Column(Boolean, default=False)` to `User` instead of hard deletes.

- **Database Backup Strategy**
  - Set up a daily `pg_dump` scheduled task (or use Supabase / Render's managed backup).

- **Connection Pooling**
  - Configure `pool_size` and `max_overflow` in `database.py` for concurrent exam loads.

### 🟢 Low Priority

- **Read Replica**
  - As load grows, route `GET` (reporting) requests to a read replica and `POST` (exam submission) to the primary.

---

## 8. Admin & Analytics Dashboard

### 🟡 Medium Priority

- **Admin Dashboard Page**
  - A protected `/admin` page showing:
    - Total candidates registered
    - Exams completed today / this week
    - Most common MBTI type
    - Average score per temperament

- **Candidate Management**
  - List all users, view their reports, and re-send reports via email.

- **Question Bank Manager**
  - CRUD interface to add/edit/delete questions without touching the database directly.

### 🟢 Low Priority

- **Aggregate Analytics**
  - MBTI type distribution charts (bar chart of all 16 types across all sessions).
  - Enneagram type prevalence pie charts.
  - Average time-to-complete per module.

- **Export to CSV / Excel**
  - Export all candidate responses and scores to a spreadsheet for offline analysis.

---

## 9. AI / ML Integrations

### 🟡 Medium Priority

- **AI-Generated Report Narrative**
  - Use an LLM (e.g., via OpenAI API) to generate a personalized, paragraph-form interpretation of the combined assessment results.
  - Replace the generic `composite_insights.personality_summary` with a dynamically generated one.

- **Career Recommendation Engine**
  - Train a simple model on (MBTI type, Temperament type, Enneagram type) → Career domain mappings.
  - Or use a rules-based expert system as a first step.

### 🟢 Low Priority

- **Anomaly Detection**
  - Flag responses that look inconsistent or rushed (e.g., all answered in < 5 seconds per question).
  - Add a `reliability_score` to the report.

- **Clustering Similar Profiles**
  - Group candidates by personality clusters to provide peer comparison insights ("You think similarly to 23% of candidates in this database").

---

## 10. Deployment & DevOps

### 🔴 High Priority

- **Environment Configuration**
  - Move all secrets out of `.env` and use a proper secrets manager (e.g., Railway secrets, Render environment variables) in production.

- **Production WSGI/ASGI Setup**
  - Replace `uvicorn` dev server with `gunicorn + uvicorn workers` for production.
  ```bash
  gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
  ```

### 🟡 Medium Priority

- **Containerization (Docker)**
  - Create a `Dockerfile` and `docker-compose.yml` bundling the FastAPI app + PostgreSQL for easy local setup and cloud deployment.

- **CI/CD Pipeline**
  - Use GitHub Actions to auto-run linting, tests, and Alembic migrations on each push to `main`.

- **Automated Testing**
  - Write `pytest` tests for all scoring modules (`scoring_mbti.py`, `scoring_temperament.py`).
  - Add API integration tests for `/questions`, `/submit-exam`, and `/api/report/{id}`.

### 🟢 Low Priority

- **Cloud Deployment**
  - Deploy to Railway, Render, or AWS EC2.
  - Use Neon or Supabase for managed PostgreSQL.

- **CDN for Static Files**
  - Serve `frontend/static/` assets via a CDN (e.g., Cloudflare) for faster load times globally.

---

## Priority Summary

| Priority | Count | Theme |
|----------|-------|-------|
| 🔴 High   | 12    | Known gaps, broken features, missing data persistence |
| 🟡 Medium | 20    | UX polish, new modules, API robustness |
| 🟢 Low    | 14    | Advanced features, AI, scale, optimization |

---

## Suggested Implementation Order

1. Fix **Temperament in Report** + wire up `report.html` to real data
2. Implement **Enneagram & Brain Dominance Scoring**
3. Fix **Real MBTI Cognitive Functions** and **Quiz Duration**
4. Add **`country` to User model** via Alembic
5. Implement **Session Resume** via `localStorage`
6. Add **Question Navigation Map** on `session.html`
7. Enable **PDF Export** for reports
8. Add **Admin Authentication** and route protection
9. Add **Multiple Intelligences** module
10. Set up **Docker + CI/CD** for deployment readiness

---

*This document is a living roadmap. Update it as features are implemented or reprioritized.*
