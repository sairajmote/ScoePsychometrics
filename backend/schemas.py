from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class QuestionBase(BaseModel):
    id: int
    category: str
    text: str
    options: Dict[str, Optional[str]]
    keyed: Optional[str] = None
    correct_answer: str

class TestResultBase(BaseModel):
    student_name: str
    test_type: str
    score: int

class TraitScore(BaseModel):
    total: int
    count: int
    average: float

class TraitResults(BaseModel):
    personality: Dict[str, TraitScore]
    cognitive: Dict[str, TraitScore]

class SubmitTestRequest(BaseModel):
    student_name: str
    results: TraitResults
