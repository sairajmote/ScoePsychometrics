from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class QuestionBase(BaseModel):
    id: int
    category: str
    subtest: Optional[str] = None
    text: str
    options: Dict[str, Optional[str]]
    keyed: Optional[str] = None
    correct_answer: Optional[str] = None

class ResponseItem(BaseModel):
    question_id: int
    selected_option: str # "A", "B", "C", "D", "E", "F", "G"

class SubmitExamRequest(BaseModel):
    student_name: str
    email: str
    country: Optional[str] = None
    password: Optional[str] = None
    education: Optional[str] = None
    quiz_duration_seconds: Optional[int] = 0
    responses: List[ResponseItem]

class ExamSubmissionResponse(BaseModel):
    status: str
    report_id: str
    user_id: int
    session_id: int
    temperament_type: Optional[str] = None
    temperament_description: Optional[str] = None
    big5_profile: Optional[str] = None
    enneagram_type: Optional[str] = None
    enneagram_label: Optional[str] = None
    enneagram_description: Optional[str] = None

class GoogleAuthRequest(BaseModel):
    credential: str


# ── Feedback schemas ────────────────────────────────────────────────────────

class FeedbackSubmit(BaseModel):
    """Payload sent by the browser when a user submits the feedback survey."""
    # Optional linking fields
    user_id:   Optional[int]  = None
    report_id: Optional[str]  = None

    # Q1-Q14 quantitative (None = question was skipped)
    q1_overall_accuracy:     Optional[int] = None  # Likert 1-5
    q2_personality_accuracy: Optional[int] = None  # Likert 1-5
    q3_trait_scores_accuracy: Optional[int] = None  # Likert 1-5
    q4_self_understanding:   Optional[int] = None  # Likert 1-5
    q5_report_clarity:       Optional[int] = None  # Likert 1-5
    q6_trust:                Optional[int] = None  # Likert 1-5
    q7_novelty:              Optional[int] = None  # Likert 1-5
    q8_ei_agreement:         Optional[int] = None  # 1=Yes / 0=No
    q9_mi_agreement:         Optional[int] = None  # 1=Yes / 0=No
    q10_enneagram_agreement: Optional[int] = None  # 1=Yes / 0=No
    q11_test_length:         Optional[int] = None  # Likert 1-5
    q12_recommend:           Optional[int] = None  # Likert 1-5
    q13_retake:              Optional[int] = None  # 1=Yes / 0=No
    q14_satisfaction:        Optional[int] = None  # Likert 1-5

    # Q15 – open-ended
    q15_open_text: Optional[str] = None


class FeedbackStatsResponse(BaseModel):
    """Aggregated statistics returned by GET /api/feedback/stats."""
    total_responses: int
    overall_accuracy_score: float          # 0-100 %
    per_metric_averages: Dict[str, Optional[float]]
    open_text_samples: List[Optional[str]] # last 5 non-empty responses
