# ScoePsychometrics — Technical Explanation

## What is this project?

ScoePsychometrics is a web-based psychometric assessment platform. It administers
multi-section personality and cognitive questionnaires, records candidate responses in a
PostgreSQL database, computes personality scores, and generates a structured PDF-ready
report — all served through a single FastAPI backend with Jinja2 HTML templates.

---

## Project Structure

```
psycho_one/
├── backend/
│   ├── __init__.py
│   ├── database.py          # SQLAlchemy engine + session factory
│   ├── main.py              # FastAPI app — routes, API endpoints, scoring orchestration
│   ├── models.py            # ORM table definitions (User, Question, QuizSession, Response, Report)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── scoring_mbti.py      # MBTI scoring logic (dichotomy percentages, type label)
│   ├── seed_mbti.py         # One-time DB seeder for 98 MBTI questions
│   └── seed_temperament.py  # One-time DB seeder for 57 Eysenck temperament questions
│
├── frontend/
│   ├── static/
│   │   ├── css/style.css    # Global stylesheet (monochrome brutalist design)
│   │   ├── js/script.js     # Global JS (scroll reveal animations, nav effects)
│   │   └── img/             # Logo and static assets
│   └── templates/           # Jinja2 HTML templates
│       ├── index.html        # Landing / home page
│       ├── exam.html         # Exam overview & instructions page
│       ├── session.html      # Active quiz page (JS-driven, fetches questions via API)
│       ├── report.html       # Candidate report viewer
│       └── sample_report.html# Static demo report with charts (Chart.js)
│
├── alembic/                 # DB migration scripts (Alembic)
├── alembic.ini
├── seed_questions.py        # Legacy seeder (Cognitive Abilities + Personality Traits)
├── requirements.txt
└── .env                     # DATABASE_URL and other secrets
```

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.11+ / FastAPI | REST API + HTML page serving |
| **ORM** | SQLAlchemy | Database abstraction |
| **Migrations** | Alembic | Schema versioning |
| **Database** | PostgreSQL | Persistent storage for users, questions, responses, reports |
| **Templates** | Jinja2 | Server-rendered HTML pages |
| **Frontend** | Vanilla HTML/CSS/JS | Exam UI, charts, animations |
| **Charts** | Chart.js | Radar + bar charts in the sample report |
| **Config** | python-dotenv | Loads `.env` into `os.environ` |
| **Server** | Uvicorn | ASGI server (`uvicorn backend.main:app --reload --port 8001`) |

---

## Database Schema

### `users`
Stores one row per candidate.

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | Auto-increment |
| `name` | String(200) | Candidate's full name |
| `email` | String(255) | Unique; used to de-duplicate returning candidates |
| `education` | String(200) | Optional education level |
| `created_at` | DateTime TZ | Server default (`now()`) |

### `questions`
Master table for all question content — shared across all test modules.

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | Auto-increment |
| `category` | String(100) | `"mbti"`, `"temperament"`, `"Cognitive Abilities"`, `"Personality Traits"` |
| `subtest` | String(100) | Dimension code e.g. `"EI"`, `"SN"`, `"EI_temperament"`, `"N_temperament"` |
| `text` | Text | Question body |
| `option_a`–`option_g` | String(500) | Answer options; unused slots are `NULL` |
| `keyed` | String(5) | `"+"` or `"-"` — scoring direction |
| `correct_answer` | String(5) | `"A"–"G"` — the answer that earns the point (or `NULL`) |
| `created_at` | DateTime TZ | Auto |

### `quiz_sessions`
One row per exam sitting.

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `user_id` | FK → users | |
| `status` | String(20) | `"in_progress"` / `"completed"` |
| `started_at` | DateTime TZ | |
| `completed_at` | DateTime TZ | Set on submission |
| `duration_seconds` | Integer | Optional |

### `responses`
One row per question answered per session.

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `session_id` | FK → quiz_sessions | |
| `question_id` | FK → questions | |
| `selected_option` | String(5) | `"A"`–`"G"` |
| `answered_at` | DateTime TZ | |

### `reports`
Stores the full scored report as a JSON blob.

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `report_id` | String(50) | Human-readable ID e.g. `"RPT-2026-0323-A4B1"` |
| `user_id` | FK → users | |
| `session_id` | FK → quiz_sessions | |
| `report_data` | JSON | Complete report structure (mirroring `sample_report_data.json`) |
| `created_at` | DateTime TZ | |

---

## Seeding Workflow

Seeders are standalone Python scripts run once from the project root.

```powershell
# Activate the virtual environment first
.venv\Scripts\Activate.ps1

# Seed MBTI questions (98 questions, 7-point Likert)
python backend/seed_mbti.py

# Seed Eysenck Temperament questions (57 questions, Yes/Maybe/No)
python backend/seed_temperament.py
```

Each seeder:
1. Deletes all rows for its `category` from `responses` (FK safety).
2. Deletes all rows for its `category` from `questions`.
3. Inserts fresh question rows with the correct `subtest`, `option_*`, `keyed`,
   and `correct_answer` values.
4. Commits and closes the session.

---

## API Endpoints

### `GET /`
Returns `index.html` — the landing page.

### `GET /exam`
Returns `exam.html` — overview of the assessment modules and instructions.

### `GET /session`
Returns `session.html` — the interactive quiz UI.

### `GET /questions?category=<cat>`
Returns a JSON array of all questions for the given category.

**Response shape (per question):**
```json
{
  "id": 42,
  "category": "temperament",
  "subtest": "EI_temperament",
  "text": "Do you often feel a craving for new experiences?",
  "options": { "A": "Yes", "B": "Maybe", "C": "No" },
  "keyed": "+",
  "correct_answer": "A"
}
```

### `POST /submit-exam`
Accepts `SubmitExamRequest` — the candidate's name, email, and all responses —
then orchestrates the full pipeline:

1. **Upsert user** by email.
2. **Create a `QuizSession`** record.
3. **Save every `Response`** row.
4. **Score MBTI** via `scoring_mbti.score_mbti()`.
5. **Build the `report_data` JSON** blob.
6. **Persist a `Report`** row.
7. Returns `{ status, report_id, user_id, session_id }`.

### `GET /api/report/{report_id}`
Fetches and returns the raw `report_data` JSON for a given report ID.

### `GET /report`
Returns `report.html` — reads `report_id` from the query string, calls
`/api/report/{id}` via client-side JS, and renders the report.

---

## Assessment Modules

### MBTI (Myers-Briggs Type Indicator)
- **98 questions** across 4 dichotomies: EI, SN, TF, JP.
- **Format:** 7-point Likert (Strongly Disagree → Strongly Agree), options A–G.
- **Scoring** (`scoring_mbti.py`):
  - Each response is mapped to an option index (1–7).
  - `keyed="+"` questions: index > 4 → pole A; index < 4 → pole B.
  - `keyed="-"` questions: reversed.
  - Percentage scores are computed per dichotomy to determine the winning pole.
  - A 4-letter type string (e.g. `"INTJ"`) is produced.

### Temperament (Eysenck Personality Questionnaire)
- **57 questions** based on the EPQ-R instrument developed by Hans Eysenck.
- **Format:** Yes / Maybe / No, options A / B / C.
- **Three dimensions measured:**

| Subtest Code | Dimension | Meaning |
|---|---|---|
| `EI_temperament` | Extraversion (E) | Sociability, impulsiveness, liveliness |
| `N_temperament` | Neuroticism (N) | Emotional instability, anxiety, moodiness |
| `LIE_temperament` | Lie (L) scale | Social desirability / response validity check |

- **Temperament classification** (not yet wired to the report — scoring logic to be added):

| High E + Low N | → Sanguine |
|---|---|
| High E + High N | → Choleric |
| Low E + Low N | → Phlegmatic |
| Low E + High N | → Melancholic |

> Q34 ("Do you enjoy work that requires concentration?") carries **no points** for
> any answer — it is included solely as a distractor/buffer question.

---

## Frontend Quiz Flow (`session.html`)

1. **Page load:** `loadData()` fires two parallel `fetch()` calls:
   - `GET /questions?category=mbti`
   - `GET /questions?category=temperament`
2. **Grouping:** Questions are grouped by `category` → two tabs: **MBTI** and **TEMPERAMENT**.
3. **Rendering:**
   - Questions with **≥ 5 options** → 7-point Likert scale UI.
   - Questions with **≤ 3 options** → Yes / Maybe / No pill-style radio buttons.
   - Questions with **4 options** → Standard labelled radio grid (legacy MCQ path).
4. **Tab navigation:** Previous / Next buttons step through domain tabs; a progress bar tracks position.
5. **Submission:** `submitExam()` gathers all checked radio values, prompts for name + email,
   and `POST`s to `/submit-exam`. On success, it redirects to `/report?id=<report_id>`.

---

## Migrations

Schema changes are tracked with Alembic.

```powershell
# Create a new migration after editing models.py
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head
```

The `.ini` file points to `DATABASE_URL` from the environment.

---

## Running Locally

```powershell
# 1. Activate venv
.venv\Scripts\Activate.ps1

# 2. Apply migrations
alembic upgrade head

# 3. Seed questions
python backend/seed_mbti.py
python backend/seed_temperament.py

# 4. Start dev server
uvicorn backend.main:app --reload --port 8001
```

Navigate to `http://localhost:8001`.
