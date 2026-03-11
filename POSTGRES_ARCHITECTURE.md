# PostgreSQL Architecture & Data Flow

This document explains why PostgreSQL was chosen as the primary database for the Psycho project and how data flows through the system from the first question to the final report.

## Why PostgreSQL?

1.  **Relational Integrity**: As a psychometric platform, data consistency is critical. Foreign keys ensure that every response belongs to a valid question and a valid quiz session.
2.  **JSONB Support**: PostgreSQL's native JSON support allows us to store the finalized, high-resolution report as a single document while keeping the raw response data relational.
3.  **Scalability**: Handles thousands of concurrent quiz-takers with ease, unlike SQLite.
4.  **Advanced Queries**: Enables complex analytical queries (e.g., "What is the average Agreeableness score for students in B.Tech Computer Science?").

---

## Database Schema (The Models)

We have implemented five core tables in `backend/models.py`:

| Table | Purpose | Key Columns |
| :--- | :--- | :--- |
| **Users** | Identity & Demographics | `id`, `name`, `email`, `education` |
| **Questions** | The 142-question bank | `id`, `category`, `subtest`, `text`, `options` |
| **QuizSessions** | Tracking a single test attempt | `id`, `user_id`, `status` (in_progress/completed) |
| **Responses** | Individual answers (the "Raw" data) | `id`, `session_id`, `question_id`, `selected_option` |
| **Reports** | The finalized Psychometric Report | `id`, `user_id`, `report_data` (Full JSON Blob) |

---

## Data Flow: From Start to Finish

### 1. Initialization (Backend)
-   Questions are seeded into the **Questions** table.
-   The frontend fetches questions via `GET /questions` to render the exam.

### 2. The Quiz Journey (Frontend → Backend)
-   **Start**: When a user enters their name/email, a record is created in **Users** and a new **QuizSession** starts.
-   **Progress**: As the user answers questions, their selections are sent to the backend and saved in the **Responses** table. This ensures no data is lost if the tab is accidentally closed.

### 3. The "Scoring" Event (Backend Logic)
When the student clicks "Submit":
1.  Backend marks the **QuizSession** as `completed`.
2.  Backend pulls all **Responses** for that session.
3.  Scoring algorithms (Big Five, MBTI, Enneagram, etc.) process the raw answers.
4.  A comprehensive JSON object is generated (containing all chart data and interpretations).
5.  This JSON is saved into the **Reports** table, linked to the `user_id`.

### 4. Report Rendering (Frontend)
1.  The user is redirected to `/report?id=RPT-XXX`.
2.  The `report.html` page fetches the JSON blob from `GET /api/report/{id}`.
3.  JavaScript (Chart.js) reads the JSON and renders the colorful, interactive report you see.

---

## Future Analytics
Because raw responses are stored individually in the **Responses** table, we can later perform item-level analysis (e.g., "Which question do most 'Extroverts' skip?") without needing to re-run the whole test.
