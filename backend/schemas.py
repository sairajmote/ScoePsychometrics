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

