"""
seed_brain_dominance.py
Seeds 40 Brain Dominance questions using a 5-point Likert scale.
Scale: Strongly Disagree / Disagree / Neutral / Agree / Strongly Agree

Scoring keys (stored in the `keyed` column):
  "L" → Left-brain tendency  (odd-numbered questions: 1,3,5,…,39)
  "R" → Right-brain tendency (even-numbered questions: 2,4,6,…,40)

Run from the project root with the virtual environment active:
    (.venv) PS Z:\\projects\\Psycho\\psycho_one> python backend/seed_brain_dominance.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend import models


QUESTIONS_TEXT = [
    "When faced with a problem, I rely on logic and reasoning above everything else.",          # 1
    "I tend to leave my belongings scattered around rather than putting them away.",            # 2
    "I would much rather take a mathematics class than an art or pottery class.",               # 3
    "I often dive straight into a task without bothering to read the instructions first.",      # 4
    "I believe that important decisions should always be grounded in facts and logical reasoning.", # 5
    "I have a vivid imagination and spend a lot of time in my own inner world.",               # 6
    "I plan my life carefully and approach things in a logical, methodical way.",               # 7
    "I tend to follow my intuition rather than thinking things through step by step.",          # 8
    "I handle situations in a calm, objective manner rather than letting emotions take over.",  # 9
    "I would describe myself as a creative person who needs a regular creative outlet.",        # 10
    "I almost never show up late — punctuality is something I take seriously.",                 # 11
    "I prefer variety and spontaneity in life over having a fixed routine.",                    # 12
    "I make decisions based on hard facts and evidence, not on how I feel at the time.",       # 13
    "I frequently daydream and find my mind wandering off into fantasy.",                       # 14
    "I behave in a businesslike, organised manner in most situations.",                         # 15
    "I enjoy letting my imagination run wild and exploring flights of fantasy.",                # 16
    "I could not live comfortably in a messy or disorganised environment.",                     # 17
    "I tend to do things in a half-hearted or incomplete way rather than seeing them through.", # 18
    "I listen to my brain rather than my heart when making important choices.",                 # 19
    "I regularly forget to put things back in their proper place after using them.",            # 20
    "I rarely cry or get emotional during sad films or moving stories.",                        # 21
    "I need to have music playing in the background when I am working or studying.",            # 22
    "I tend to think deeply and quietly rather than talking through my thoughts out loud.",     # 23
    "I believe strongly in the importance of art and creative expression in the world.",        # 24
    "I am not easily unsettled or disturbed by unexpected events or bad news.",                 # 25
    "I tend to rebel against rules and resist being told what to do.",                          # 26
    "I approach most situations in a calm and composed way, even under pressure.",              # 27
    "I enjoy abstract art and am drawn to things that are open to interpretation.",             # 28
    "I rarely feel the need for praise or validation from other people.",                       # 29
    "I consider myself a romantic person who is deeply in touch with my emotions.",             # 30
    "I tend to be sceptical and like to question claims before accepting them as true.",        # 31
    "I regularly come up with new ideas and find fresh ways of looking at things.",             # 32
    "I never travel or go anywhere without having a clear plan in place beforehand.",           # 33
    "I often make a mess of things and find it hard to stay organised.",                        # 34
    "I prefer to work with numbers, data, and concrete information.",                           # 35
    "I tend to leave tasks half finished or let my responsibilities slide.",                    # 36
    "I am calm and steady even in tense or high-pressure situations.",                          # 37
    "I find it easy to get stressed out and overwhelmed by things.",                            # 38
    "I behave in a structured, methodical way and take my duties seriously.",                   # 39
    "I am a totally random, unpredictable person who rarely does things the same way twice.",   # 40
]

# Tendency key for each question (index 0 = question 1).
# Odd questions → Left (L), Even questions → Right (R)
QUESTION_KEYS = [
    "L", "R", "L", "R", "L", "R", "L", "R", "L", "R",  # 1–10
    "L", "R", "L", "R", "L", "R", "L", "R", "L", "R",  # 11–20
    "L", "R", "L", "R", "L", "R", "L", "R", "L", "R",  # 21–30
    "L", "R", "L", "R", "L", "R", "L", "R", "L", "R",  # 31–40
]


def seed_brain_dominance_questions():
    db = SessionLocal()

    # Clear existing brain_dominance questions
    bd_ids = db.query(models.Question.id).filter(models.Question.category == "brain_dominance")
    db.query(models.Response).filter(
        models.Response.question_id.in_(bd_ids)
    ).delete(synchronize_session=False)
    deleted = db.query(models.Question).filter(
        models.Question.category == "brain_dominance"
    ).delete(synchronize_session=False)
    if deleted > 0:
        print(f"Cleared {deleted} existing Brain Dominance questions.")

    print(f"Seeding {len(QUESTIONS_TEXT)} Brain Dominance questions...")

    for idx, text in enumerate(QUESTIONS_TEXT):
        q = models.Question(
            category="brain_dominance",
            subtest=None,
            text=text,
            option_a="Strongly Disagree",
            option_b="Disagree",
            option_c="Neutral",
            option_d="Agree",
            option_e="Strongly Agree",
            keyed=QUESTION_KEYS[idx],
            correct_answer=None,
        )
        db.add(q)

    db.commit()
    print("Brain Dominance seeding complete.")
    db.close()


if __name__ == "__main__":
    seed_brain_dominance_questions()
