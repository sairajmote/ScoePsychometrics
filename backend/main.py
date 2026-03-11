from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
from . import models, database, schemas
from .database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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

@app.get("/questions", response_model=list[schemas.QuestionBase])
async def get_questions(db: Session = Depends(get_db)):
    questions = db.query(models.Question).all()
    # Explicitly return dictionaries that match QuestionBase
    return [
        {
            "id": q.id,
            "category": q.category,
            "text": q.text,
            "options": {
                "A": q.option_a,
                "B": q.option_b,
                "C": q.option_c,
                "D": q.option_d,
                "E": q.option_e,
            },
            "keyed": q.keyed,
            "correct_answer": q.correct_answer,
        }
        for q in questions
    ]

@app.post("/submit-results")
async def submit_results(request: schemas.SubmitTestRequest, db: Session = Depends(get_db)):
    try:
        # Calculate a total score (e.g., sum of personality trait scores)
        total_score = sum(trait.total for trait in request.results.personality.values())
        
        # Save to database
        new_result = models.TestResult(
            student_name=request.student_name,
            test_type="Comprehensive Assessment",
            score=int(total_score)
        )
        db.add(new_result)
        db.commit()
        db.refresh(new_result)
        
        return {"status": "success", "result_id": new_result.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
