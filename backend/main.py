"""
Main entry point for the Psychometric Assessment Platform backend.
Handles all API routes, database sessions, and assessment scoring.
"""
import os
import uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from . import models, database, schemas, auth, scoring_mbti, scoring_temperament, scoring_big5, scoring_brain_dominance, scoring_multiple_intelligence, scoring_enneagram, insights_engine
from .database import engine, get_db

# Initialize FastAPI application
app = FastAPI(title="Psycho One - Psychometric Platform")

# Tables are managed by Alembic migrations — run: alembic upgrade head

# Get the absolute path of the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend", "static")), name="static")

# Setup templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "frontend", "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@app.get("/exam", response_class=HTMLResponse)
async def read_exam(request: Request):
    return templates.TemplateResponse(request=request, name="exam.html", context={})

@app.get("/session", response_class=HTMLResponse)
async def read_session(request: Request):
    return templates.TemplateResponse(request=request, name="session.html", context={})

@app.get("/report", response_class=HTMLResponse)
async def read_report(request: Request):
    return templates.TemplateResponse(request=request, name="report.html", context={})

@app.get("/sample-report", response_class=HTMLResponse)
async def read_sample_report(request: Request):
    return templates.TemplateResponse(request=request, name="sample_report.html", context={})

@app.get("/health-db")
async def health_db(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@app.post("/auth/google-verify")
async def google_verify(request: schemas.GoogleAuthRequest):
    idinfo = auth.verify_google_token(request.credential)
    if not idinfo:
        raise HTTPException(status_code=400, detail="Invalid Google token")
    
    return {
        "status": "success",
        "email": idinfo.get("email"),
        "name": idinfo.get("name"),
        "picture": idinfo.get("picture")
    }

@app.post("/submit-exam", response_model=schemas.ExamSubmissionResponse)
async def submit_exam(request: schemas.SubmitExamRequest, db: Session = Depends(get_db)):
    try:
        # 1. Get or Create User
        user = db.query(models.User).filter(models.User.email == request.email).first()
        if not user:
            user = models.User(
                name=request.student_name,
                email=request.email,
                education=request.education,
                country=request.country,
                password=request.password
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            if request.password and not user.password:
                user.password = request.password
            if request.country and not user.country:
                user.country = request.country
            db.commit()

        # 2. Create Quiz Session
        session = models.QuizSession(
            user_id=user.id,
            status="completed",
            duration_seconds=request.quiz_duration_seconds,
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
        enneagram_scoring_data = []

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
                elif q.category == "enneagram":
                    enneagram_scoring_data.append({
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
        enneagram_results = scoring_enneagram.score_enneagram(enneagram_scoring_data)
        
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
                "quiz_duration_seconds": request.quiz_duration_seconds or 0,
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
                    "cognitive_functions": scoring_mbti.get_cognitive_stack(mbti_results["result_type"]),
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
                },
                "enneagram": {
                    "label": "Enneagram Personality Type",
                    "description": "The Enneagram identifies core motivations, fears, and behavioral patterns across nine personality types.",
                    "primary_type": enneagram_results["primary_type"],
                    "center": enneagram_results["center"],
                    "type_scores": enneagram_results["type_scores"],
                    "type_rankings": enneagram_results["type_rankings"],
                    "interpretation": enneagram_results["interpretation"]
                },
                "temperament": {
                    "label": "Core Temperament",
                    "description": "Your biological temperament based on Eysenck's Personality Theory, measuring Extraversion and emotional stability.",
                    "result_type": temperament_results["temperament_type"],
                    "interpretation": temperament_results["description"],
                    "e_score": temperament_results["e_score"],
                    "n_score": temperament_results["n_score"],
                    "e_max": temperament_results["e_max"],
                    "n_max": temperament_results["n_max"],
                }
            },
            "composite_insights": {
                **insights_engine.generate_ai_insights(
                    mbti_results=mbti_results,
                    temperament_results=temperament_results,
                    enneagram_results=enneagram_results,
                    big5_results=big5_results,
                    brain_dominance_results=brain_dominance_results,
                    mi_results=mi_results
                )
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
            "big5_profile": big5_results["profile_summary"],
            "enneagram_type": enneagram_results["primary_type"]["code"],
            "enneagram_label": enneagram_results["primary_type"]["label"],
            "enneagram_description": enneagram_results["interpretation"]
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

@app.get("/api/reports/user/{email}")
async def get_reports_by_email(email: str, password: Optional[str] = None, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return []

    if user.password != password:
        raise HTTPException(status_code=401, detail="Invalid password")

    reports = db.query(models.Report).filter(models.Report.user_id == user.id).order_by(models.Report.created_at.desc()).all()
    
    result = []
    for r in reports:
        result.append({
            "report_id": r.report_id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "candidate_name": user.name
        })
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
