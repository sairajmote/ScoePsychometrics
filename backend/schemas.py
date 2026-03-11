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
    education: Optional[str] = None
    responses: List[ResponseItem]

class ExamSubmissionResponse(BaseModel):
    status: str
    report_id: str
    user_id: int
    session_id: int
