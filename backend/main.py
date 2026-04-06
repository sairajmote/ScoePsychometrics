from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import os
import uuid
from datetime import datetime
from . import models, database, schemas, scoring_mbti, scoring_temperament, scoring_big5, scoring_brain_dominance, scoring_multiple_intelligence
from .database import engine, get_db

app = FastAPI()

# Tables are managed by Alembic migrations — run: alembic upgrade head

# Get the absolute path of the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend", "static")), name="static")

# Setup templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "frontend", "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/exam", response_class=HTMLResponse)
async def read_exam(request: Request):
    return templates.TemplateResponse("exam.html", {"request": request})

@app.get("/session", response_class=HTMLResponse)
async def read_session(request: Request):
    return templates.TemplateResponse("session.html", {"request": request})

@app.get("/report", response_class=HTMLResponse)
async def read_report(request: Request):
    return templates.TemplateResponse("report.html", {"request": request})

@app.get("/sample-report", response_class=HTMLResponse)
async def read_sample_report(request: Request):
    return templates.TemplateResponse("sample_report.html", {"request": request})

@app.get("/health-db")
async def health_db(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from typing import Optional

@app.get("/questions", response_model=list[schemas.QuestionBase])
async def get_questions(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Question)
    if category:
        query = query.filter(models.Question.category == category)
    questions = query.all()
    result = []
    for q in questions:
        # Build options dict dynamically
        opts = {
            "A": q.option_a,
            "B": q.option_b,
            "C": q.option_c,
            "D": q.option_d,
            "E": q.option_e,
        }
        if q.option_f: opts["F"] = q.option_f
        if q.option_g: opts["G"] = q.option_g
        
        result.append({
            "id": q.id,
            "category": q.category,
            "subtest": q.subtest,
            "text": q.text,
            "options": opts,
            "keyed": q.keyed,
            "correct_answer": q.correct_answer,
        })
    return result

@app.post("/submit-exam", response_model=schemas.ExamSubmissionResponse)
async def submit_exam(request: schemas.SubmitExamRequest, db: Session = Depends(get_db)):
    try:
        # 1. Get or Create User
        user = db.query(models.User).filter(models.User.email == request.email).first()
        if not user:
            user = models.User(
                name=request.student_name,
                email=request.email,
                education=request.education
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 2. Create Quiz Session
        session = models.QuizSession(
            user_id=user.id,
            status="completed",
            completed_at=func.now()
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # 3. Save Responses and prepare for scoring
        option_map = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}
        mbti_scoring_data = []
        temperament_scoring_data = []
        big5_scoring_data = []
        brain_dominance_scoring_data = []
        mi_scoring_data = []

        for item in request.responses:
            # Save raw response
            resp = models.Response(
                session_id=session.id,
                question_id=item.question_id,
                selected_option=item.selected_option
            )
            db.add(resp)

            # Fetch question details for scoring
            q = db.query(models.Question).filter(models.Question.id == item.question_id).first()
            if q:
                if q.category == "mbti":
                    mbti_scoring_data.append({
                        "subtest": q.subtest,
                        "keyed": q.keyed,
                        "selected_option_index": option_map.get(item.selected_option, 4)
                    })
                elif q.category == "temperament":
                    temperament_scoring_data.append({
                        "subtest": q.subtest,
                        "correct_answer": q.correct_answer,
                        "selected_option": item.selected_option
                    })
                elif q.category == "big5":
                    big5_scoring_data.append({
                        "subtest": q.subtest,
                        "keyed": q.keyed,
                        "selected_option": item.selected_option
                    })
                elif q.category == "brain_dominance":
                    brain_dominance_scoring_data.append({
                        "keyed": q.keyed,
                        "selected_option": item.selected_option
                    })
                elif q.category == "multiple_intelligence":
                    mi_scoring_data.append({
                        "subtest": q.subtest,
                        "selected_option": item.selected_option
                    })

        db.commit()

        # 4. Score MBTI
        mbti_results = scoring_mbti.score_mbti(mbti_scoring_data)

        # 4b. Score Temperament
        temperament_results = scoring_temperament.score_temperament(temperament_scoring_data)

        # 4c. Score Big 5
        big5_results = scoring_big5.score_big5(big5_scoring_data)

        # 4d. Score Brain Dominance
        brain_dominance_results = scoring_brain_dominance.score_brain_dominance(brain_dominance_scoring_data)

        # 4e. Score Multiple Intelligence
        mi_results = scoring_multiple_intelligence.score_multiple_intelligence(mi_scoring_data)
        
        # 5. Build full Report JSON
        report_id = f"RPT-{datetime.now().strftime('%Y-%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        
        # Mocking other subtests since we are only doing MBTI now
        report_data = {
            "meta": {
                "report_id": report_id,
                "candidate": {
                    "name": user.name,
                    "email": user.email,
                    "education": user.education or "Not Specified"
                },
                "generated_at": datetime.now().isoformat(),
                "quiz_duration_seconds": 1200, # Mocked
                "total_questions_answered": len(request.responses)
            },
            "subtests": {
                "mbti": {
                    "label": "Myers-Briggs Type Indicator",
                    "description": "Assessment of how people perceive the world and make decisions.",
                    "result_type": mbti_results["result_type"],
                    "type_label": scoring_mbti.get_mbti_label(mbti_results["result_type"]),
                    "dichotomies": {
                        "EI": {
                            "dimension_a": {"label": "Extraversion", "code": "E", "score": mbti_results["dimensions"]["EI"]["pct_a"]},
                            "dimension_b": {"label": "Introversion", "code": "I", "score": mbti_results["dimensions"]["EI"]["pct_b"]}
                        },
                        "SN": {
                            "dimension_a": {"label": "Sensing", "code": "S", "score": mbti_results["dimensions"]["SN"]["pct_a"]},
                            "dimension_b": {"label": "Intuition", "code": "N", "score": mbti_results["dimensions"]["SN"]["pct_b"]}
                        },
                        "TF": {
                            "dimension_a": {"label": "Thinking", "code": "T", "score": mbti_results["dimensions"]["TF"]["pct_a"]},
                            "dimension_b": {"label": "Feeling", "code": "F", "score": mbti_results["dimensions"]["TF"]["pct_b"]}
                        },
                        "JP": {
                            "dimension_a": {"label": "Judging", "code": "J", "score": mbti_results["dimensions"]["JP"]["pct_a"]},
                            "dimension_b": {"label": "Perceiving", "code": "P", "score": mbti_results["dimensions"]["JP"]["pct_b"]}
                        }
                    },
                    "cognitive_functions": {
                        "dominant": {"label": "Mock Function", "code": "Xi", "strength": 80},
                        "auxiliary": {"label": "Mock Function", "code": "Xe", "strength": 60},
                        "tertiary": {"label": "Mock Function", "code": "Xi", "strength": 40},
                        "inferior": {"label": "Mock Function", "code": "Xe", "strength": 20}
                    },
                    "interpretation": "Your personality profile suggests a unique way of processing information and interacting with the world."
                },
                "big5": {
                    "label": "Big Five Personality Traits",
                    "description": "The Big Five model measures five core personality dimensions that predict behaviour across work, relationships, and life.",
                    "profile_summary": big5_results["profile_summary"],
                    "traits": big5_results["traits"]
                },
                "brain_dominance": {
                    "label": "Brain Dominance",
                    "description": "Measures the relative strength of left-brain (analytical/logical) and right-brain (creative/intuitive) tendencies.",
                    "left":      brain_dominance_results["left"],
                    "right":     brain_dominance_results["right"],
                    "dominance": brain_dominance_results["dominance"],
                },
                "multiple_intelligence": {
                    "label": "Multiple Intelligence",
                    "description": "Howard Gardner's theory identifies nine distinct intelligences that reflect diverse cognitive strengths and learning styles.",
                    "profile_summary":       mi_results["profile_summary"],
                    "dominant_intelligences": mi_results["dominant_intelligences"],
                    "dominant_labels":        mi_results["dominant_labels"],
                    "intelligences":          mi_results["intelligences"],
                }
            },
            "composite_insights": {
                "personality_summary": (
                    f"Your MBTI personality type is **{mbti_results['result_type']}** — "
                    f"{scoring_mbti.get_mbti_label(mbti_results['result_type'])}. "
                    "This profile reflects your natural preferences for how you perceive the world and make decisions. "
                    "Use the dichotomy breakdown below to understand the clarity of each dimension."
                ),
                "top_strengths": [
                    f"Strong {mbti_results['result_type'][0]} preference (Energy dimension)",
                    "Analytical decision-making",
                    "Consistent personal values",
                    "Structured thinking"
                ],
                "growth_areas": [
                    "Balancing opposing preferences",
                    "Adapting to new perspectives",
                    "Exploring less dominant traits"
                ],
                "recommended_career_domains": [
                    "Research & Strategy",
                    "Technology & Engineering",
                    "Counseling & Psychology",
                    "Writing & Communication"
                ]
            }
        }

        # 6. Save Report
        new_report = models.Report(
            report_id=report_id,
            user_id=user.id,
            session_id=session.id,
            report_data=report_data
        )
        db.add(new_report)
        db.commit()

        return {
            "status": "success",
            "report_id": report_id,
            "user_id": user.id,
            "session_id": session.id,
            "temperament_type": temperament_results["temperament_type"],
            "temperament_description": temperament_results["description"],
            "big5_profile": big5_results["profile_summary"]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/report/{report_id}")
async def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(models.Report).filter(models.Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.report_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
