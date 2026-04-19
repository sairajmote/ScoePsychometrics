from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=True)
    education = Column(String(200), nullable=True)
    country = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), index=True)       # e.g. "big_five", "mbti", "enneagram"
    subtest = Column(String(100), nullable=True)      # e.g. "openness", "extraversion"
    text = Column(Text, nullable=False)
    option_a = Column(String(500), nullable=False)
    option_b = Column(String(500), nullable=False)
    option_c = Column(String(500), nullable=False)
    option_d = Column(String(500), nullable=False)
    option_e = Column(String(500), nullable=True)
    option_f = Column(String(500), nullable=True)
    option_g = Column(String(500), nullable=True)
    keyed = Column(String(5), nullable=True)          # "+" or "-" for personality traits
    correct_answer = Column(String(5), nullable=True) # "A", "B", "C", "D" or "E"
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="in_progress")  # in_progress, completed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("quiz_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option = Column(String(5), nullable=False)  # "A", "B", "C", "D", "E"
    answered_at = Column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g. "RPT-2026-0311-A7X9"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("quiz_sessions.id"), nullable=False)
    report_data = Column(JSON, nullable=False)  # The full JSON blob (same structure as sample_report_data.json)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Feedback(Base):
    """
    Stores one feedback submission per user per report.
    Q1–Q14 are quantitative (Likert 1–5 or Yes/No 0–1).
    Q15 is the open-ended text response.
    """
    __tablename__ = "feedback"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=True)
    report_id  = Column(String(50), ForeignKey("reports.report_id"), nullable=True)

    # Q1  Overall result accuracy (Likert 1–5)
    q1_overall_accuracy    = Column(Integer, nullable=True)
    # Q2  Personality type accuracy (Likert 1–5)
    q2_personality_accuracy = Column(Integer, nullable=True)
    # Q3  Trait-score accuracy (Likert 1–5)
    q3_trait_scores_accuracy = Column(Integer, nullable=True)
    # Q4  Usefulness for self-understanding (Likert 1–5)
    q4_self_understanding  = Column(Integer, nullable=True)
    # Q5  Clarity of the report (Likert 1–5)
    q5_report_clarity      = Column(Integer, nullable=True)
    # Q6  Trust in the test (Likert 1–5)
    q6_trust               = Column(Integer, nullable=True)
    # Q7  Surprise / novelty (Likert 1–5)
    q7_novelty             = Column(Integer, nullable=True)
    # Q8  Agreement with Extraversion/Introversion result (Yes=1 / No=0)
    q8_ei_agreement        = Column(Integer, nullable=True)
    # Q9  Agreement with dominant intelligence result (Yes=1 / No=0)
    q9_mi_agreement        = Column(Integer, nullable=True)
    # Q10 Agreement with Enneagram type (Yes=1 / No=0)
    q10_enneagram_agreement = Column(Integer, nullable=True)
    # Q11 Test length / fatigue (Likert 1–5, 5 = too long)
    q11_test_length        = Column(Integer, nullable=True)
    # Q12 Likelihood to recommend (Likert 1–5)
    q12_recommend          = Column(Integer, nullable=True)
    # Q13 Would take the test again (Yes=1 / No=0)
    q13_retake             = Column(Integer, nullable=True)
    # Q14 Overall satisfaction (Likert 1–5)
    q14_satisfaction       = Column(Integer, nullable=True)
    # Q15 Open-ended additional comments
    q15_open_text          = Column(Text, nullable=True)

    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
