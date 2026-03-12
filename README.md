#  ScopePsychometrics

> *Know thyself. A comprehensive personality test . FOR FREE*

---

## What is this?

ScopePsychometrics is a **free, comprehensive personality assessment** that goes way deeper than those 10-minute quizzes you find floating around the internet. We're talking ~500 carefully constructed questions powered by **Item Response Theory (IRT)** — the same psychometric framework used in serious academic research.

By the time you're done, you'll walk away with a full breakdown of:

-  **MBTI Personality Type** — yes, we know you've already done this on 3 other sites
-  **Temperament Profile** — dig into the *why* behind how you tick
-  **Enneagram** — your core motivations, fears, and growth paths
-  **Other cool psychometric goodies** — because why stop there?
-  **Career Recommendations** — tailored to your actual personality, not vibes

---

## Tech Stack

| Layer     | Tech          |
|-----------|---------------|
| Backend   | FastAPI   |
| Scoring   | R (IRT-based)  |
| Frontend  | Vanilla JS  |

Lean, fast, and no unnecessary bloat — just like a good personality test should be.

---

## Scoring & Methodology

We currently use **Classical Test Theory (CTT)** for scoring. We're planning to move to IRT-based scoring down the line — but that needs a decent dataset first, which we'll be building up through your responses over time. So every test you take is genuinely helping make the next version better. 

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL database

### Setup
1. Clone the repository and navigate to the project root directory.
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On macOS/Linux
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the `.env` file in the root directory with your database connection string, for example:
   ```env
   DATABASE_URL=postgresql://postgres:testing@localhost:5432/psycho_db
   ```
5. Run database migrations to set up the necessary tables (if you haven't already):
   ```bash
   alembic upgrade head
   ```

### Running the Application
1. Seed the database with the initial MBTI questions:
   ```bash
   python backend/seed_mbti.py
   ```
2. Start the FastAPI development server:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
3. Open your browser and navigate to `http://127.0.0.1:8000`.
   - View the exam home at `/`
   - Take the assessment at `/session`
   - View the sample report at `/sample-report`
