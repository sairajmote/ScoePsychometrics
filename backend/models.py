from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base

class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, index=True)
    test_type = Column(String)
    score = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)   # e.g. "Cognitive", "Personality"
    text = Column(String, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    option_e = Column(String, nullable=True)
    keyed = Column(String, nullable=True)  # "+" or "-" for personality traits
    correct_answer = Column(String, nullable=False)  # "A", "B", "C", "D" or "E"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
