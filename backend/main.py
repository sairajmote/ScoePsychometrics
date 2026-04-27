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

from . import models, database, schemas, auth, scoring_mbti, scoring_temperament, scoring_big5, scoring_brain_dominance, scoring_multiple_intelligence, scoring_enneagram, insights_engine, scoring_short_form
from .database import engine, get_db
from sqlalchemy import func as sqlfunc

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

@app.post("/submit-short-form", response_model=schemas.ExamSubmissionResponse)
async def submit_short_form(request: schemas.SubmitExamRequest, db: Session = Depends(get_db)):
    """
    Submit and score the 150-question short-form assessment.
    Works identically to /submit-exam but routes all questions through
    scoring_short_form.score_short_form().
    """
    try:
        # 1. Get or create user
        user = db.query(models.User).filter(models.User.email == request.email).first()
        if not user:
            user = models.User(
                name=request.student_name,
                email=request.email,
                education=request.education,
                country=request.country,
                password=request.password,
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

        # 2. Create quiz session
        session = models.QuizSession(
            user_id=user.id,
            status="completed",
            duration_seconds=request.quiz_duration_seconds,
            completed_at=func.now(),
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # 3. Save responses and build scoring payload
        option_map = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}

        # Subtest → section mapping (mirrors seed_short_form.py)
        _SUBTEST_TO_SECTION = {
            "openness":         "big5",
            "neuroticism":      "big5",
            "agreeableness":    "big5",
            "extraversion":     "big5",
            "conscientiousness": "big5",
            "E1": "enneagram", "E2": "enneagram", "E3": "enneagram",
            "E4": "enneagram", "E5": "enneagram", "E6": "enneagram",
            "E7": "enneagram", "E8": "enneagram", "E9": "enneagram",
            "L": "brain_dominance",
            "R": "brain_dominance",
            "EI_temperament":  "temperament",
            "N_temperament":   "temperament",
            "LIE_temperament": "temperament",
            "EI": "mbti",
            "SN": "mbti",
            "TF": "mbti",
            "JP": "mbti",
            "LI":   "multiple_intelligence",
            "LMI":  "multiple_intelligence",
            "MI":   "multiple_intelligence",
            "BKI":  "multiple_intelligence",
            "SVI":  "multiple_intelligence",
            "IPI":  "multiple_intelligence",
            "INPI": "multiple_intelligence",
            "NI":   "multiple_intelligence",
        }

        scoring_payload = []

        for item in request.responses:
            resp = models.Response(
                session_id=session.id,
                question_id=item.question_id,
                selected_option=item.selected_option,
            )
            db.add(resp)

            q = db.query(models.Question).filter(
                models.Question.id == item.question_id
            ).first()
            if q and q.category == "short_form":
                section = _SUBTEST_TO_SECTION.get(q.subtest or "", "")
                # Existential Intelligence shares the "EI" key with MBTI:
                # override section when MI block (no keyed +/- numeric sense for MI)
                if q.subtest == "EI" and q.option_a == "Strongly Disagree" and q.option_g is None:
                    section = "multiple_intelligence"

                scoring_payload.append({
                    "subtest":         q.subtest,
                    "keyed":           q.keyed,
                    "correct_answer":  q.correct_answer,
                    "selected_option": item.selected_option,
                    "selected_option_index": option_map.get(item.selected_option, 4),
                    "section":         section,
                })

        db.commit()

        # 4. Score everything
        results = scoring_short_form.score_short_form(scoring_payload)

        mbti_res    = results["mbti"]
        enn_res     = results["enneagram"]
        big5_res    = results["big5"]
        bd_res      = results["brain_dominance"]
        mi_res      = results["multiple_intelligence"]
        temp_res    = results["temperament"]

        # 5. Build report
        report_id = f"RPT-SF-{datetime.now().strftime('%Y-%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        report_data = {
            "meta": {
                "report_id":               report_id,
                "form_type":               "short_150",
                "candidate": {
                    "name":      user.name,
                    "email":     user.email,
                    "education": user.education or "Not Specified",
                },
                "generated_at":             datetime.now().isoformat(),
                "quiz_duration_seconds":    request.quiz_duration_seconds or 0,
                "total_questions_answered": len(request.responses),
            },
            "subtests": {
                "mbti": {
                    "label":       "Myers-Briggs Type Indicator",
                    "description": "Assessment of how people perceive the world and make decisions.",
                    "result_type": mbti_res["result_type"],
                    "type_label":  scoring_mbti.get_mbti_label(mbti_res["result_type"]),
                    "dichotomies": {
                        "EI": {
                            "dimension_a": {"label": "Extraversion", "code": "E", "score": mbti_res["dimensions"]["EI"]["pct_a"]},
                            "dimension_b": {"label": "Introversion", "code": "I", "score": mbti_res["dimensions"]["EI"]["pct_b"]},
                        },
                        "SN": {
                            "dimension_a": {"label": "Sensing",    "code": "S", "score": mbti_res["dimensions"]["SN"]["pct_a"]},
                            "dimension_b": {"label": "Intuition",  "code": "N", "score": mbti_res["dimensions"]["SN"]["pct_b"]},
                        },
                        "TF": {
                            "dimension_a": {"label": "Thinking", "code": "T", "score": mbti_res["dimensions"]["TF"]["pct_a"]},
                            "dimension_b": {"label": "Feeling",  "code": "F", "score": mbti_res["dimensions"]["TF"]["pct_b"]},
                        },
                        "JP": {
                            "dimension_a": {"label": "Judging",    "code": "J", "score": mbti_res["dimensions"]["JP"]["pct_a"]},
                            "dimension_b": {"label": "Perceiving", "code": "P", "score": mbti_res["dimensions"]["JP"]["pct_b"]},
                        },
                    },
                    "cognitive_functions": scoring_mbti.get_cognitive_stack(mbti_res["result_type"]),
                },
                "big5": {
                    "label":           "Big Five Personality Traits",
                    "description":     "Five core personality dimensions.",
                    "profile_summary": big5_res["profile_summary"],
                    "traits":          big5_res["traits"],
                },
                "enneagram": {
                    "label":         "Enneagram Personality Type",
                    "description":   "Nine core motivations and behavioral patterns.",
                    "primary_type":  enn_res["primary_type"],
                    "center":        enn_res["center"],
                    "type_scores":   enn_res["type_scores"],
                    "type_rankings": enn_res["type_rankings"],
                    "interpretation": enn_res["interpretation"],
                },
                "brain_dominance": {
                    "label":       "Brain Dominance",
                    "description": "Relative strength of left vs. right brain tendencies.",
                    "left":        bd_res["left"],
                    "right":       bd_res["right"],
                    "dominance":   bd_res["dominance"],
                },
                "temperament": {
                    "label":         "Core Temperament (EPQ)",
                    "description":   "Eysenck extraversion and neuroticism profile.",
                    "result_type":   temp_res["temperament_type"],
                    "interpretation": temp_res["description"],
                    "e_score":       temp_res["e_score"],
                    "n_score":       temp_res["n_score"],
                    "e_max":         temp_res["e_max"],
                    "n_max":         temp_res["n_max"],
                },
                "multiple_intelligence": {
                    "label":                 "Multiple Intelligence",
                    "description":           "Howard Gardner's nine intelligences.",
                    "profile_summary":       mi_res["profile_summary"],
                    "dominant_intelligences": mi_res["dominant_intelligences"],
                    "dominant_labels":       mi_res["dominant_labels"],
                    "intelligences":         mi_res["intelligences"],
                },
            },
            "composite_insights": {
                **insights_engine.generate_ai_insights(
                    mbti_results=mbti_res,
                    temperament_results=temp_res,
                    enneagram_results=enn_res,
                    big5_results=big5_res,
                    brain_dominance_results=bd_res,
                    mi_results=mi_res,
                )
            },
        }

        # 6. Save report
        new_report = models.Report(
            report_id=report_id,
            user_id=user.id,
            session_id=session.id,
            report_data=report_data,
        )
        db.add(new_report)
        db.commit()

        return {
            "status":                    "success",
            "report_id":                 report_id,
            "user_id":                   user.id,
            "session_id":                session.id,
            "temperament_type":          temp_res["temperament_type"],
            "temperament_description":   temp_res["description"],
            "big5_profile":              big5_res["profile_summary"],
            "enneagram_type":            enn_res["primary_type"]["code"],
            "enneagram_label":           enn_res["primary_type"]["label"],
            "enneagram_description":     enn_res["interpretation"],
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)


# ════════════════════════════════════════════════════════
# FEEDBACK ROUTES
# ════════════════════════════════════════════════════════

@app.get("/feedback", response_class=HTMLResponse)
async def read_feedback(request: Request):
    """Serve the feedback survey page."""
    return templates.TemplateResponse(request=request, name="feedback.html", context={})


@app.post("/api/feedback")
async def submit_feedback(payload: schemas.FeedbackSubmit, db: Session = Depends(get_db)):
    """
    Persist one user's survey answers.
    All quantitative fields are optional; missing values are stored as NULL
    and excluded from aggregate calculations.
    """
    try:
        entry = models.Feedback(
            user_id   = payload.user_id,
            report_id = payload.report_id,
            q1_overall_accuracy      = payload.q1_overall_accuracy,
            q2_personality_accuracy  = payload.q2_personality_accuracy,
            q3_trait_scores_accuracy = payload.q3_trait_scores_accuracy,
            q4_self_understanding    = payload.q4_self_understanding,
            q5_report_clarity        = payload.q5_report_clarity,
            q6_trust                 = payload.q6_trust,
            q7_novelty               = payload.q7_novelty,
            q8_ei_agreement          = payload.q8_ei_agreement,
            q9_mi_agreement          = payload.q9_mi_agreement,
            q10_enneagram_agreement  = payload.q10_enneagram_agreement,
            q11_test_length          = payload.q11_test_length,
            q12_recommend            = payload.q12_recommend,
            q13_retake               = payload.q13_retake,
            q14_satisfaction         = payload.q14_satisfaction,
            q15_open_text            = payload.q15_open_text,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return {"status": "success", "feedback_id": entry.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/feedback/stats", response_model=schemas.FeedbackStatsResponse)
async def get_feedback_stats(db: Session = Depends(get_db)):
    """
    Compute real-time aggregated feedback statistics.

    Overall Accuracy Score (0–100%) methodology:
    ───────────────────────────────────────────────────────────────────
    • Likert 1-5 questions: normalised to 0-100 as (avg-1)/4 * 100
    • Yes/No questions (0 or 1): already 0-100 when multiplied by 100
    • Q11 (fatigue) is INVERTED before inclusion (5=max fatigue → bad)
    • Weights applied before averaging:
        - Accuracy questions (Q1,Q2,Q3):           weight 3 each
        - Usefulness / satisfaction (Q4,Q14):       weight 2 each
        - Clarity / trust / recommend (Q5,Q6,Q12): weight 2 each
        - Self-consistency (Q8,Q9,Q10):             weight 1 each
        - Novelty (Q7), retake (Q13):               weight 1 each
        - Fatigue Q11 (inverted):                   weight 1
    • Missing/NULL values: that question is excluded from numerator
      AND denominator, so partial responses don't bias the score.
    """
    rows = db.query(models.Feedback).all()
    total = len(rows)

    if total == 0:
        return schemas.FeedbackStatsResponse(
            total_responses=0,
            overall_accuracy_score=0.0,
            per_metric_averages={},
            open_text_samples=[]
        )

    # ———  Helper: mean of a column, ignoring NULLs  ———
    def col_avg(attr: str) -> Optional[float]:
        vals = [getattr(r, attr) for r in rows if getattr(r, attr) is not None]
        return round(sum(vals) / len(vals), 3) if vals else None

    # ———  Per-metric averages (raw scale)  ———
    # Q1-Q5: 1-10 scale   |   Q6,Q7,Q11,Q12,Q14: 1-5 scale
    likert10_cols = [
        "q1_overall_accuracy", "q2_personality_accuracy", "q3_trait_scores_accuracy",
        "q4_self_understanding", "q5_report_clarity",
    ]
    likert5_cols = [
        "q6_trust", "q7_novelty", "q11_test_length", "q12_recommend", "q14_satisfaction"
    ]
    likert_cols = likert10_cols + likert5_cols   # all Likert (for type-check)
    yn_cols = ["q8_ei_agreement", "q9_mi_agreement", "q10_enneagram_agreement", "q13_retake"]

    per_metric: dict = {}
    for col in likert_cols + yn_cols:
        per_metric[col] = col_avg(col)

    # ———  Weighted Overall Accuracy Score  ———
    WEIGHTS = {
        "q1_overall_accuracy":     3,
        "q2_personality_accuracy": 3,
        "q3_trait_scores_accuracy": 3,
        "q4_self_understanding":   2,
        "q5_report_clarity":       2,
        "q6_trust":                2,
        "q7_novelty":              1,
        "q8_ei_agreement":         1,
        "q9_mi_agreement":         1,
        "q10_enneagram_agreement": 1,
        "q11_test_length":         1,   # inverted below
        "q12_recommend":           2,
        "q13_retake":              1,
        "q14_satisfaction":        2,
    }

    total_weight = 0.0
    weighted_sum = 0.0

    for col, w in WEIGHTS.items():
        avg = per_metric.get(col)
        if avg is None:
            continue
        if col in likert10_cols:
            pct = (avg - 1) / 9 * 100   # Likert 1-10 -> 0-100
        elif col in likert5_cols:
            pct = (avg - 1) / 4 * 100   # Likert 1-5  -> 0-100
            if col == "q11_test_length":
                pct = 100 - pct         # Invert fatigue so higher = better
        else:
            pct = avg * 100             # Yes/No 0-1  -> 0-100
        weighted_sum += pct * w
        total_weight += w

    oas = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0

    # ———  Last 5 open-text comments  ———
    samples = [
        r.q15_open_text for r in reversed(rows)
        if r.q15_open_text and r.q15_open_text.strip()
    ][:5]

    return schemas.FeedbackStatsResponse(
        total_responses=total,
        overall_accuracy_score=oas,
        per_metric_averages=per_metric,
        open_text_samples=samples
    )




def mask_db_url(url: str) -> str:
    """Masks the password part of a database connection string."""
    if not url: return "NOT_SET"
    import re
    # Matches the password between : and @
    return re.sub(r":([^/@]+)@", ":***@", url)

@app.get("/debug")
def debug():
    """Diagnostic endpoint to verify environment configuration on Azure."""
    return {
        "db": mask_db_url(os.getenv("DATABASE_URL")),
        "has_key": bool(os.getenv("GEMINI_API_KEY"))
    }