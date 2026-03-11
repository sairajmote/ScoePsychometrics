r"""
seed_questions.py
Run from the project root (with .venv activated) to seed 80 psychometric questions.
Includes 50 personality traits and 30 cognitive items (25 cognitive failures + 5 logic/math).
Clears existing questions first so re-runs are safe.

  (.venv) PS Z:\projects\Psycho\psycho_one> python seed_questions.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from backend.database import SessionLocal, engine
from backend import models

# Drop and recreate tables to apply schema changes
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

PERS_LIKERT = {
    "option_a": "Strongly Disagree",
    "option_b": "Disagree",
    "option_c": "Neutral",
    "option_d": "Agree",
    "option_e": "Strongly Agree"
}

COG_LIKERT = {
    "option_a": "Never",
    "option_b": "Rarely",
    "option_c": "Occasionally",
    "option_d": "Frequently",
    "option_e": "Always"
}

# The 50-item personality scoring key sequence (+/-)
PERSONALITY_KEY_SEQ = "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+---+-+---+-+--+++++--+-++-+"

QUESTIONS = [
    # ── Cognitive Abilities (25 Cognitive Failures + 5 Original logic/math) ──────────────────
    # User's Cognitive Failures (Likert 1-5)
    { "category": "Cognitive Abilities", "text": "(Forgetfulness) Read something without thinking about it and must re-read?", **COG_LIKERT, "keyed": "+", "correct_answer": "D" },
    { "category": "Cognitive Abilities", "text": "(Forgetfulness/False Triggering) Forget why you moved from one room to another?", **COG_LIKERT, "keyed": "+", "correct_answer": "D" },
    { "category": "Cognitive Abilities", "text": "(False Triggering) Fail to notice road signposts?", **COG_LIKERT, "keyed": "+", "correct_answer": "D" },
    { "category": "Cognitive Abilities", "text": "(Cognitive) Confuse right and left when giving directions?", **COG_LIKERT, "keyed": "+", "correct_answer": "D" },
    { "category": "Cognitive Abilities", "text": "(Forgetfulness/False Triggering) Bump into people?", **COG_LIKERT, "keyed": "+", "correct_answer": "D" },
    { "category": "Cognitive Abilities", "text": "(False Triggering) Forget whether you've turned off a light/fire or locked the door?", **COG_LIKERT, "keyed": "+", "correct_answer": "D" },
    { "category": "Cognitive Abilities", "text": "(Forgetfulness) Forget people's names when being introduced?", **COG_LIKERT, "keyed": "+", "correct_answer": "D" },
    { "category": "Cognitive Abilities", "text": "(Distractibility) Say something that could be taken as insulting?", **COG_LIKERT, "keyed": "+", "correct_answer": "D" },
    { "category": "Cognitive Abilities", "text": "(Distractibility) Fail to hear people when doing something else?", **COG_LIKERT, "keyed": "+", "correct_answer": "C" },
    { "category": "Cognitive Abilities", "text": "(Distractibility) Lose your temper and regret it?", **COG_LIKERT, "keyed": "+", "correct_answer": "C" },
    { "category": "Cognitive Abilities", "text": "(Distractibility) Leave important letters unanswered for days?", **COG_LIKERT, "keyed": "+", "correct_answer": "C" },
    { "category": "Cognitive Abilities", "text": "(False Triggering) Forget which way to turn on a rarely-used familiar road?", **COG_LIKERT, "keyed": "+", "correct_answer": "C" },
    { "category": "Cognitive Abilities", "text": "(Cognitive) Fail to spot something in a supermarket even though it's there?", **COG_LIKERT, "keyed": "+", "correct_answer": "C" },
    { "category": "Cognitive Abilities", "text": "(Distractibility) Wonder whether you've used a word correctly?", **COG_LIKERT, "keyed": "+", "correct_answer": "C" },
    { "category": "Cognitive Abilities", "text": "(Cognitive) Have trouble making up your mind?", **COG_LIKERT, "keyed": "+", "correct_answer": "B" },
    { "category": "Cognitive Abilities", "text": "(Cognitive) Forget appointments?", **COG_LIKERT, "keyed": "+", "correct_answer": "B" },
    { "category": "Cognitive Abilities", "text": "(Forgetfulness) Forget where you put something like a book or newspaper?", **COG_LIKERT, "keyed": "+", "correct_answer": "B" },
    { "category": "Cognitive Abilities", "text": "(False Triggering) Accidentally throw away the wrong thing?", **COG_LIKERT, "keyed": "+", "correct_answer": "B" },
    { "category": "Cognitive Abilities", "text": "(Distractibility) Daydream when you should be listening?", **COG_LIKERT, "keyed": "+", "correct_answer": "B" },
    { "category": "Cognitive Abilities", "text": "(Forgetfulness) Forget people's names?", **COG_LIKERT, "keyed": "+", "correct_answer": "B" },
    { "category": "Cognitive Abilities", "text": "(Distractibility) Start one task and get distracted into doing another?", **COG_LIKERT, "keyed": "+", "correct_answer": "B" },
    { "category": "Cognitive Abilities", "text": "(Forgetfulness) Have something \"on the tip of your tongue\" but can't recall it?", **COG_LIKERT, "keyed": "+", "correct_answer": "B" },
    { "category": "Cognitive Abilities", "text": "(Forgetfulness/False Triggering) Forget what you came to the shops to buy?", **COG_LIKERT, "keyed": "+", "correct_answer": "B" },
    { "category": "Cognitive Abilities", "text": "(False Triggering) Drop things?", **COG_LIKERT, "keyed": "+", "correct_answer": "B" },
    { "category": "Cognitive Abilities", "text": "(Distractibility) Find you can't think of anything to say?", **COG_LIKERT, "keyed": "+", "correct_answer": "B" },
    
    # Original logic/math (MCQ) - keeping these for variety in cognitive category
    {
        "category": "Cognitive Abilities",
        "text": "If all Bloops are Razzies and all Razzies are Lazzies, are all Bloops definitely Lazzies?",
        "option_a": "Yes", "option_b": "No", "option_c": "Cannot be determined", "option_d": "Only some Bloops are Lazzies", "option_e": None,
        "keyed": None, "correct_answer": "A",
    },
    {
        "category": "Cognitive Abilities",
        "text": "If all X are Y, and no Y are Z, then no X can be Z. Is this logic valid?",
        "option_a": "Always valid", "option_b": "Never valid", "option_c": "Sometimes valid", "option_d": "Invalid argument", "option_e": None,
        "keyed": None, "correct_answer": "A",
    },
    {
        "category": "Cognitive Abilities",
        "text": "What comes next in the sequence: 2, 6, 12, 20, 30, ...?",
        "option_a": "40", "option_b": "42", "option_c": "44", "option_d": "36", "option_e": None,
        "keyed": None, "correct_answer": "B",
    },
    {
        "category": "Cognitive Abilities",
        "text": "A train travels at 60 km/h for 2.5 hours. How far does it travel?",
        "option_a": "120 km", "option_b": "140 km", "option_c": "150 km", "option_d": "160 km", "option_e": None,
        "keyed": None, "correct_answer": "C",
    },
    {
        "category": "Cognitive Abilities",
        "text": "Which shape is the odd one out: Triangle, Square, Circle, Pentagon?",
        "option_a": "Triangle", "option_b": "Square", "option_c": "Circle", "option_d": "Pentagon", "option_e": None,
        "keyed": None, "correct_answer": "C",
    },

    # ── Personality Traits (50) ── 5-point Likert Scale ──────────────────────
    { "category": "Personality Traits", "text": "(Extraversion) Am the life of the party.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Agreeableness) Feel little concern for others.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Conscientiousness) Am always prepared.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Emotional Stability) Get stressed out easily.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Intellect/Imagination) Have a rich vocabulary.", **PERS_LIKERT, "correct_answer": "D" },
    
    { "category": "Personality Traits", "text": "(Extraversion) Don't talk a lot.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Agreeableness) Am interested in people.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Conscientiousness) Leave my belongings around.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Emotional Stability) Am relaxed most of the time.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Intellect/Imagination) Have difficulty understanding abstract ideas.", **PERS_LIKERT, "correct_answer": "B" },

    { "category": "Personality Traits", "text": "(Extraversion) Feel comfortable around people.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Agreeableness) Insult people.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Conscientiousness) Pay attention to details.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Emotional Stability) Worry about things.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Intellect/Imagination) Have a vivid imagination.", **PERS_LIKERT, "correct_answer": "D" },

    { "category": "Personality Traits", "text": "(Extraversion) Keep in the background.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Agreeableness) Sympathize with others' feelings.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Conscientiousness) Make a mess of things.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Emotional Stability) Seldom feel blue.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Intellect/Imagination) Am not interested in abstract ideas.", **PERS_LIKERT, "correct_answer": "B" },

    { "category": "Personality Traits", "text": "(Extraversion) Start conversations.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Agreeableness) Am not interested in other people's problems.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Conscientiousness) Get chores done right away.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Emotional Stability) Am easily disturbed.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Intellect/Imagination) Have excellent ideas.", **PERS_LIKERT, "correct_answer": "D" },

    { "category": "Personality Traits", "text": "(Extraversion) Have little to say.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Agreeableness) Have a soft heart.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Conscientiousness) Often forget to put things back in their proper place.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Emotional Stability) Get upset easily.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Intellect/Imagination) Do not have a good imagination.", **PERS_LIKERT, "correct_answer": "B" },

    { "category": "Personality Traits", "text": "(Extraversion) Talk to a lot of different people at parties.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Agreeableness) Am not really interested in others.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Conscientiousness) Like order.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Emotional Stability) Change my mood a lot.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Intellect/Imagination) Am quick to understand things.", **PERS_LIKERT, "correct_answer": "D" },

    { "category": "Personality Traits", "text": "(Extraversion) Don't like to draw attention to myself.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Agreeableness) Take time out for others.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Conscientiousness) Shirk my duties.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Emotional Stability) Have frequent mood swings.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Intellect/Imagination) Use difficult words.", **PERS_LIKERT, "correct_answer": "D" },

    { "category": "Personality Traits", "text": "(Extraversion) Don't mind being the center of attention.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Agreeableness) Feel others' emotions.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Conscientiousness) Follow a schedule.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Emotional Stability) Get irritated easily.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Intellect/Imagination) Spend time reflecting on things.", **PERS_LIKERT, "correct_answer": "D" },

    { "category": "Personality Traits", "text": "(Extraversion) Am quiet around strangers.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Agreeableness) Make people feel at ease.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Conscientiousness) Am exacting in my work.", **PERS_LIKERT, "correct_answer": "D" },
    { "category": "Personality Traits", "text": "(Emotional Stability) Often feel blue.", **PERS_LIKERT, "correct_answer": "B" },
    { "category": "Personality Traits", "text": "(Intellect/Imagination) Am full of ideas.", **PERS_LIKERT, "correct_answer": "D" },
]

# Assign keys to personality questions
pers_idx = 0
for q in QUESTIONS:
    if q["category"] == "Personality Traits":
        if pers_idx < len(PERSONALITY_KEY_SEQ):
            q["keyed"] = PERSONALITY_KEY_SEQ[pers_idx]
            pers_idx += 1

def seed():
    db = SessionLocal()
    try:
        for q in QUESTIONS:
            db.add(models.Question(**q))
        db.commit()
        print(f"Successfully seeded {len(QUESTIONS)} questions into the database!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
