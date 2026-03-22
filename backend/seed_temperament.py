"""
seed_temperament.py
Seed the 57 Eysenck Personality Questionnaire (EPQ) / temperament questions.
Uses Yes / Maybe / No format (options A / B / C).

Run from the project root with the virtual environment active:
    (.venv) PS Z:\\projects\\Psycho\\psycho_one> python backend/seed_temperament.py

Scoring dimensions
------------------
  e  → Extraversion (mapped internally as subtest="EI_temperament")
  l  → Neuroticism  (mapped internally as subtest="N_temperament")
  n  → Lie scale    (mapped internally as subtest="LIE_temperament")

keyed field convention:
  "+"  → the answer listed in the grading key scores 1 point for that dimension
  "-"  → no point scored for any dimension (Q34 only has no valid keyed answer)
  For all questions the *scored answer* (Yes or No as per the key) is stored
  in correct_answer ("A"=Yes, "B"=Maybe, "C"=No).
"""

import os
import sys

# Allow running from the project root or from within backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend import models


# ---------------------------------------------------------------------------
# Question text (Q1–Q57 from temperament_quiz_questions.txt)
# ---------------------------------------------------------------------------
QUESTIONS_TEXT = [
    "Do you often feel a craving for new experiences, to shake things up, or to feel a thrill?",                                       # Q1
    "Do you often feel that you need friends who can understand you, encourage you, or sympathize with you?",                           # Q2
    "Do you consider yourself a carefree person?",                                                                                      # Q3
    "Is it very hard for you to give up on your intentions?",                                                                           # Q4
    "Do you think things over slowly and prefer to wait before acting?",                                                                # Q5
    "Do you always keep your promises, even when it's inconvenient for you?",                                                           # Q6
    "Do you often have mood swings — highs and lows?",                                                                                  # Q7
    "Do you usually speak and act quickly?",                                                                                            # Q8
    "Have you ever felt unhappy without any real reason for it?",                                                                       # Q9
    "Is it true that you could dare to do anything on a dare?",                                                                         # Q10
    "Do you feel shy when you want to get to know someone of the opposite sex that you like?",                                          # Q11
    "Does it ever happen that when you get angry, you lose your temper?",                                                               # Q12
    "Does it often happen that you act without thinking, on impulse?",                                                                  # Q13
    "Do you often worry about things you feel you shouldn't have done or said?",                                                        # Q14
    "Do you prefer reading books over meeting people?",                                                                                 # Q15
    "Is it true that you are easily offended?",                                                                                         # Q16
    "Do you like going out and being in company often?",                                                                                # Q17
    "Do you sometimes have thoughts you would rather not share with others?",                                                           # Q18
    "Is it true that sometimes you are so full of energy that everything goes great, but other times you feel exhausted?",              # Q19
    "Do you try to keep your social circle small, limited to your closest friends?",                                                    # Q20
    "Do you daydream a lot?",                                                                                                           # Q21
    "When someone shouts at you, do you shout back?",                                                                                   # Q22
    "Do you often feel guilty about something?",                                                                                        # Q23
    "Do you consider all your habits to be good ones?",                                                                                 # Q24
    "Are you sometimes able to let yourself go and have a great time in a lively group?",                                              # Q25
    "Would you say your nerves are often stretched to the limit?",                                                                      # Q26
    "Are you known as a lively and cheerful person?",                                                                                   # Q27
    "After something is done, do you often think back and feel you could have done it better?",                                         # Q28
    "Do you feel at ease when you're in a large group?",                                                                                # Q29
    "Do you ever pass on rumors?",                                                                                                      # Q30
    "Does it happen that you can't sleep because different thoughts keep running through your head?",                                   # Q31
    "If you want to find something out, do you prefer to look it up in a book rather than ask someone?",                               # Q32
    "Do you ever have a racing heartbeat?",                                                                                             # Q33
    "Do you enjoy work that requires concentration?",                                                                                   # Q34
    "Do you ever have fits of trembling?",                                                                                              # Q35
    "Do you always tell the truth?",                                                                                                    # Q36
    "Do you find it unpleasant to be in a group where people tease each other?",                                                       # Q37
    "Are you an irritable person?",                                                                                                     # Q38
    "Do you enjoy work that requires quick action?",                                                                                    # Q39
    "Is it true that you are often troubled by thoughts about unpleasant things and horrors that could have happened, even though everything turned out fine?",  # Q40
    "Is it true that you are slow in your movements and somewhat unhurried?",                                                           # Q41
    "Are you ever late for work or for a meeting with someone?",                                                                        # Q42
    "Do you often have nightmares?",                                                                                                    # Q43
    "Is it true that you love to talk so much that you never miss a chance to chat with a new person?",                                # Q44
    "Do you suffer from any aches or pains?",                                                                                           # Q45
    "Would you feel upset if you couldn't see your friends for a long time?",                                                           # Q46
    "Would you call yourself a nervous person?",                                                                                        # Q47
    "Are there people among your acquaintances that you clearly dislike?",                                                              # Q48
    "Would you call yourself a self-confident person?",                                                                                 # Q49
    "Are you easily hurt by criticism of your faults or your work?",                                                                   # Q50
    "Is it hard for you to genuinely enjoy events where a lot of people are present?",                                                  # Q51
    "Are you bothered by a feeling that you are somehow worse than others?",                                                            # Q52
    "Could you liven up a dull gathering?",                                                                                             # Q53
    "Does it happen that you talk about things you know nothing about?",                                                                # Q54
    "Do you worry about your health?",                                                                                                  # Q55
    "Do you like to play pranks on others?",                                                                                            # Q56
    "Do you suffer from insomnia?",                                                                                                     # Q57
]

# ---------------------------------------------------------------------------
# Grading key from temperament_quiz_questions.txt
# Format: (scored_answer, dimension)
#   scored_answer: "A" = Yes, "C" = No  (the answer that earns 1 point)
#   dimension: "EI_temperament" | "N_temperament" | "LIE_temperament" | None (no points)
# ---------------------------------------------------------------------------
GRADING_KEY = [
    ("A", "EI_temperament"),   # Q1  Yes → e:1
    ("A", "N_temperament"),    # Q2  Yes → l:1
    ("A", "EI_temperament"),   # Q3  Yes → e:1
    ("A", "N_temperament"),    # Q4  Yes → l:1
    ("C", "EI_temperament"),   # Q5  No  → e:1
    ("A", "LIE_temperament"),  # Q6  Yes → n:1
    ("A", "N_temperament"),    # Q7  Yes → l:1
    ("A", "EI_temperament"),   # Q8  Yes → e:1
    ("A", "N_temperament"),    # Q9  Yes → l:1
    ("A", "EI_temperament"),   # Q10 Yes → e:1
    ("A", "N_temperament"),    # Q11 Yes → l:1
    ("C", "N_temperament"),    # Q12 No  → l:1
    ("A", "EI_temperament"),   # Q13 Yes → e:1
    ("A", "N_temperament"),    # Q14 Yes → l:1
    ("C", "EI_temperament"),   # Q15 No  → e:1
    ("A", "N_temperament"),    # Q16 Yes → l:1
    ("A", "EI_temperament"),   # Q17 Yes → e:1
    ("C", "N_temperament"),    # Q18 No  → l:1
    ("A", "N_temperament"),    # Q19 Yes → l:1
    ("C", "EI_temperament"),   # Q20 No  → e:1
    ("A", "N_temperament"),    # Q21 Yes → l:1
    ("A", "EI_temperament"),   # Q22 Yes → e:1
    ("A", "N_temperament"),    # Q23 Yes → l:1
    ("A", "LIE_temperament"),  # Q24 Yes → n:1
    ("A", "EI_temperament"),   # Q25 Yes → e:1
    ("A", "N_temperament"),    # Q26 Yes → l:1
    ("A", "EI_temperament"),   # Q27 Yes → e:1
    ("A", "N_temperament"),    # Q28 Yes → l:1
    ("C", "EI_temperament"),   # Q29 No  → e:1   (note: "feel at ease...No→e:1" means introversion)
    ("C", "N_temperament"),    # Q30 No  → l:1
    ("A", "N_temperament"),    # Q31 Yes → l:1
    ("C", "EI_temperament"),   # Q32 No  → e:1
    ("A", "N_temperament"),    # Q33 Yes → l:1
    (None, None),              # Q34 no points for any answer
    ("A", "N_temperament"),    # Q35 Yes → l:1
    ("A", "LIE_temperament"),  # Q36 Yes → n:1
    ("C", "EI_temperament"),   # Q37 No  → e:1
    ("A", "N_temperament"),    # Q38 Yes → l:1
    ("A", "EI_temperament"),   # Q39 Yes → e:1
    ("A", "N_temperament"),    # Q40 Yes → l:1
    ("C", "EI_temperament"),   # Q41 No  → e:1
    ("C", "N_temperament"),    # Q42 No  → l:1
    ("A", "N_temperament"),    # Q43 Yes → l:1
    ("A", "EI_temperament"),   # Q44 Yes → e:1
    ("A", "N_temperament"),    # Q45 Yes → l:1
    ("A", "EI_temperament"),   # Q46 Yes → e:1
    ("C", "N_temperament"),    # Q47 No  → l:1
    ("C", "N_temperament"),    # Q48 No  → l:1
    ("A", "EI_temperament"),   # Q49 Yes → e:1
    ("A", "N_temperament"),    # Q50 Yes → l:1
    ("C", "EI_temperament"),   # Q51 No  → e:1
    ("A", "N_temperament"),    # Q52 Yes → l:1
    ("A", "EI_temperament"),   # Q53 Yes → e:1
    ("C", "N_temperament"),    # Q54 No  → l:1
    ("A", "N_temperament"),    # Q55 Yes → l:1
    ("A", "EI_temperament"),   # Q56 Yes → e:1
    ("A", "N_temperament"),    # Q57 Yes → l:1
]


def seed_temperament_questions():
    db = SessionLocal()

    # Clear existing temperament questions
    temp_ids = db.query(models.Question.id).filter(models.Question.category == "temperament")
    db.query(models.Response).filter(
        models.Response.question_id.in_(temp_ids)
    ).delete(synchronize_session=False)
    deleted = db.query(models.Question).filter(
        models.Question.category == "temperament"
    ).delete(synchronize_session=False)
    if deleted > 0:
        print(f"Cleared {deleted} existing temperament questions.")

    print(f"Seeding {len(QUESTIONS_TEXT)} temperament questions...")

    for i, (text, (scored_answer, dimension)) in enumerate(
        zip(QUESTIONS_TEXT, GRADING_KEY), start=1
    ):
        q = models.Question(
            category="temperament",
            subtest=dimension,            # e.g. "EI_temperament", "N_temperament", "LIE_temperament"
            text=text,
            option_a="Yes",
            option_b="Maybe",
            option_c="No",
            option_d="",                  # column is NOT NULL in the schema; use empty string
            option_e=None,                # nullable
            keyed="+" if scored_answer else None,
            correct_answer=scored_answer, # "A"=Yes, "C"=No, None=no points
        )
        db.add(q)

    db.commit()
    print("Temperament seeding complete.")
    db.close()


if __name__ == "__main__":
    seed_temperament_questions()
