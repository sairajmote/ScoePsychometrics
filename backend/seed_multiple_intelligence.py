"""
seed_multiple_intelligence.py
Seeds 44 Multiple Intelligence questions using a 5-point Likert scale.
Scale: Strongly Disagree / Disagree / Neutral / Agree / Strongly Agree

Scoring keys (stored in the `subtest` column):
  LI   → Linguistic Intelligence           (questions: 22, 30, 38, 41)
  LMI  → Logical-Mathematical Intelligence (questions: 3, 8, 10, 13, 20, 21, 40)
  MI   → Musical Intelligence              (questions: 2, 17, 18, 34, 42)
  BKI  → Bodily-Kinesthetic Intelligence   (questions: 6, 16, 26, 31, 44)
  SVI  → Spatial-Visual Intelligence       (questions: 12, 19, 33)
  IPI  → Interpersonal Intelligence        (questions: 4, 7, 23, 24, 32)
  INPI → Intrapersonal Intelligence        (questions: 1, 11, 14, 25, 37)
  NI   → Naturalistic Intelligence         (questions: 9, 28, 29, 35, 43)
  EI   → Existential Intelligence          (questions: 5, 15, 27, 36, 39)

Run from the project root with the virtual environment active:
    (.venv) PS Z:\\projects\\Psycho\\psycho_one> python backend/seed_multiple_intelligence.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend import models


QUESTIONS_TEXT = [
    "I like to spend time going deeper and deeper into the things that are going on within me.",         # 1  [INPI]
    "I enjoy singing or playing a musical instrument.",                                                   # 2  [MI]
    "I enjoy sequential puzzles like Rubik's cube or Sudoku.",                                           # 3  [LMI]
    "Others often come to me for support or advice.",                                                     # 4  [IPI]
    "I often contemplate questions related to theology or philosophy.",                                   # 5  [EI]
    "I don't mind getting my hands dirty from activities that involve creating, fixing, or building things.", # 6  [BKI]
    "I spend a lot of time thinking about the emotions of others.",                                       # 7  [IPI]
    "I am good with numbers.",                                                                            # 8  [LMI]
    "I like tending to gardens and plants.",                                                              # 9  [NI]
    "I like measuring or categorizing stuff.",                                                            # 10 [LMI]
    "I enjoy spending time alone, processing my own emotions and reactions to things.",                   # 11 [INPI]
    "I am good at reading maps and finding my way around unfamiliar places.",                             # 12 [SVI]
    "I have always excelled in math and science at school.",                                              # 13 [LMI]
    "It is easy for me to identify how I feel and why.",                                                  # 14 [INPI]
    "I am often pondering the meaning of life.",                                                          # 15 [EI]
    "I like dancing, sports, or working out.",                                                            # 16 [BKI]
    "I am often humming a song or tune to myself in my head.",                                           # 17 [MI]
    "Music is one of my biggest interests.",                                                              # 18 [MI]
    "I vividly remember details about furniture and the interior decoration of rooms that I've been in.", # 19 [SVI]
    "I can learn better if things are accompanied by charts, diagrams, or other technical illustrations.", # 20 [LMI]
    "I enjoy challenges that require lateral thinking, like chess.",                                      # 21 [LMI]
    "I enjoy learning new words and/or languages.",                                                       # 22 [LI]
    "I am good at mediating disputes or conflicts between individuals.",                                  # 23 [IPI]
    "I am good at making a good impression when meeting new people.",                                     # 24 [IPI]
    "I spend a lot of time reflecting on my own reactions to things.",                                    # 25 [INPI]
    "I find it easiest to solve problems when my body is in motion.",                                    # 26 [BKI]
    "Questions like 'Where is humanity heading?' or 'Why are we here?' are of interest to me.",          # 27 [EI]
    "I like taking long walks in nature, alone or with my friends.",                                     # 28 [NI]
    "I feel the most alive when I am in contact with nature.",                                            # 29 [NI]
    "I am interested in writing poetry, quotes, stories, or journals.",                                  # 30 [LI]
    "I am interested in sports.",                                                                         # 31 [BKI]
    "I am good at detecting dishonesty in others.",                                                       # 32 [IPI]
    "I am better at remembering faces than names.",                                                       # 33 [SVI]
    "I am always discovering new kinds of music.",                                                        # 34 [MI]
    "I am usually good with animals.",                                                                    # 35 [NI]
    "I keep going over deep questions about life and existence that seem foolish to others.",             # 36 [EI]
    "I spend a lot of time analyzing my own emotions and reactions.",                                    # 37 [INPI]
    "I often look things up in the dictionary.",                                                          # 38 [LI]
    "I enjoy learning about how the various world religions have attempted to answer 'the big questions'.", # 39 [EI]
    "I draw charts and tables to help me think.",                                                         # 40 [LMI]
    "I love reading.",                                                                                    # 41 [LI]
    "I can tell when a note is off-key.",                                                                 # 42 [MI]
    "I enjoy learning about different species of plants and animals.",                                    # 43 [NI]
    "I like sewing, carving, model-building, or other activities that involve dexterity.",               # 44 [BKI]
]

# Intelligence subtest key for each question (index 0 = question 1)
QUESTION_SUBTESTS = [
    "INPI",  # 1
    "MI",    # 2
    "LMI",   # 3
    "IPI",   # 4
    "EI",    # 5
    "BKI",   # 6
    "IPI",   # 7
    "LMI",   # 8
    "NI",    # 9
    "LMI",   # 10
    "INPI",  # 11
    "SVI",   # 12
    "LMI",   # 13
    "INPI",  # 14
    "EI",    # 15
    "BKI",   # 16
    "MI",    # 17
    "MI",    # 18
    "SVI",   # 19
    "LMI",   # 20
    "LMI",   # 21
    "LI",    # 22
    "IPI",   # 23
    "IPI",   # 24
    "INPI",  # 25
    "BKI",   # 26
    "EI",    # 27
    "NI",    # 28
    "NI",    # 29
    "LI",    # 30
    "BKI",   # 31
    "IPI",   # 32
    "SVI",   # 33
    "MI",    # 34
    "NI",    # 35
    "EI",    # 36
    "INPI",  # 37
    "LI",    # 38
    "EI",    # 39
    "LMI",   # 40
    "LI",    # 41
    "MI",    # 42
    "NI",    # 43
    "BKI",   # 44
]


def seed_multiple_intelligence_questions():
    db = SessionLocal()

    # Clear existing multiple_intelligence questions
    mi_ids = db.query(models.Question.id).filter(models.Question.category == "multiple_intelligence")
    db.query(models.Response).filter(
        models.Response.question_id.in_(mi_ids)
    ).delete(synchronize_session=False)
    deleted = db.query(models.Question).filter(
        models.Question.category == "multiple_intelligence"
    ).delete(synchronize_session=False)
    if deleted > 0:
        print(f"Cleared {deleted} existing Multiple Intelligence questions.")

    print(f"Seeding {len(QUESTIONS_TEXT)} Multiple Intelligence questions...")

    for idx, text in enumerate(QUESTIONS_TEXT):
        q = models.Question(
            category="multiple_intelligence",
            subtest=QUESTION_SUBTESTS[idx],
            text=text,
            option_a="Strongly Disagree",
            option_b="Disagree",
            option_c="Neutral",
            option_d="Agree",
            option_e="Strongly Agree",
            keyed=None,
            correct_answer=None,
        )
        db.add(q)

    db.commit()
    print("Multiple Intelligence seeding complete.")
    db.close()


if __name__ == "__main__":
    seed_multiple_intelligence_questions()
