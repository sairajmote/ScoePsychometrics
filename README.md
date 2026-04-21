# ScopePsychometrics

> *Know thyself. A comprehensive personality test. FOR FREE*

---

## What is this?

ScopePsychometrics is a **free, comprehensive personality assessment** that goes deeper than quick online quizzes. It includes about 500 carefully crafted questions to give you detailed insights into your personality.

By the end, you'll get a full breakdown of:

- **MBTI Personality Type** — your personality preferences
- **Temperament Profile** — how you naturally behave
- **Enneagram** — your core motivations and growth areas
- **Other personality insights** — including career recommendations based on your results

---

## Tech Stack

| Layer     | Tech          |
|-----------|---------------|
| Backend   | FastAPI       |
| Scoring   | Python        |
| Frontend  | Vanilla JS    |
| Database  | PostgreSQL    |

Simple, fast, and focused — just like a good personality test.

---

## Scoring & Methodology

We use **Classical Test Theory (CTT)** for scoring, which is a reliable method for personality assessments. This ensures accurate and consistent results based on your responses.

## Assessments Included

The platform covers a wide range of personality assessments:

- **MBTI (Myers-Briggs Type Indicator)**: 16 personality types based on preferences in four dichotomies.
- **Big 5 Personality Traits**: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism.
- **Enneagram**: Nine personality types focusing on core motivations and fears.
- **Temperament**: Four temperaments (Sanguine, Choleric, Melancholic, Phlegmatic).
- **Multiple Intelligence**: Based on Howard Gardner's theory.
- **Brain Dominance**: Left-brain vs. right-brain thinking styles.
- **Short Form Assessments**: Quick versions for faster insights.

## How It Works

1. **Sign Up/Login**: Use Google Sign-In for easy access.
2. **Take the Assessment**: Answer a series of questions across different categories.
3. **Scoring**: Your responses are scored using validated algorithms.
4. **View Report**: Get a detailed report with your personality profile and recommendations.
5. **Secure Storage**: Reports are stored securely and can be accessed anytime with a password.

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL database
- Google Cloud Console Project (for Google Sign-In)

### Setup
1. Clone the repository and go to the project root.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root with your database details and Google Client ID:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/psycho_db
   GOOGLE_CLIENT_ID=your_client_id_here
   ```
5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

### Running the Application
1. Add the assessment questions to the database:
   ```bash
   python seed_questions.py
   ```
2. Start the server:
   ```bash
   uvicorn backend.main:app --reload --port 8001
   ```
3. Open `http://localhost:8001` in your browser.

### Testing
To run tests (if available):
```bash
pytest
```

## Key Features

- **Google Sign-In**: Easy and secure login for enrollment and accessing reports.
- **Multi-Vector Analysis**: Comprehensive coverage of multiple personality models for a holistic view.
- **Secure Reports**: Password-protected reports that are easy to find and retrieve.
- **Responsive Design**: Works well on desktop and mobile devices.
- **Data Privacy**: User data is handled securely with encryption.
- **Career Recommendations**: Tailored suggestions based on your personality profile.
- **Feedback System**: Users can provide feedback on their reports.

## API Endpoints

The backend provides RESTful APIs for various functionalities:

- `POST /auth/login`: User authentication
- `GET /questions`: Retrieve assessment questions
- `POST /submit`: Submit responses and get scores
- `GET /report/{id}`: Fetch user reports

For full API documentation, refer to the FastAPI auto-generated docs at `/docs` when running the server.

## Deployment

For production deployment, see the [Azure Hosting Guide](AZURE_HOSTING_GUIDE.md) for instructions on deploying to Azure.

## Contributing

We welcome contributions! Please see the contributing guidelines (if available) or open an issue for feature requests.

## Future Plans

Check out [FUTURE_IMPLEMENTATIONS.md](FUTURE_IMPLEMENTATIONS.md) for upcoming features and improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
