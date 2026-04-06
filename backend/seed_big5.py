"""
seed_big5.py
Seeds 50 Big 5 Personality questions using a 5-point Likert scale.
Scale: Strongly Disagree / Disagree / Neutral / Agree / Strongly Agree
No grading applied — questions are stored without scoring keys.

Run from the project root with the virtual environment active:
    (.venv) PS Z:\\projects\\Psycho\\psycho_one> python backend/seed_big5.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend import models


QUESTIONS_TEXT = [
    # Openness to Experience (1-10)
    "When confronted with unfamiliar perspectives that challenge long-held beliefs, I feel intellectually energized rather than defensive.",
    "I rarely see value in exploring ideas that have no immediate practical application.",
    "Abstract discussions about philosophy, art, or theoretical possibilities tend to capture my attention more than routine conversations.",
    "I prefer familiar patterns of thinking over experimenting with unconventional viewpoints.",
    "Encountering ambiguous or complex problems usually stimulates curiosity in me rather than frustration.",
    "I feel uncomfortable when conversations drift into imaginative or speculative territories.",
    "I am naturally inclined to reinterpret everyday experiences through creative or symbolic meanings.",
    "Novel experiences often seem unnecessarily disruptive to an otherwise efficient routine.",
    "I frequently find myself mentally exploring 'what if' scenarios beyond immediate reality.",
    "I see little benefit in questioning traditions or long-standing methods that already function adequately.",
    # Neuroticism (11-20)
    "Minor setbacks can remain on my mind long after the situation has passed.",
    "I rarely dwell on stressful situations once they are resolved.",
    "Unexpected uncertainty tends to trigger noticeable tension in my thoughts.",
    "Emotional fluctuations rarely influence how I approach daily responsibilities.",
    "I sometimes anticipate negative outcomes even when circumstances appear stable.",
    "I generally remain calm even when several problems arise simultaneously.",
    "Criticism can linger in my mind longer than compliments.",
    "I usually recover quickly from embarrassment or mistakes.",
    "Situations outside my control occasionally provoke persistent worry.",
    "I tend to maintain emotional steadiness even during demanding periods.",
    # Agreeableness (21-30)
    "When disagreements arise, I instinctively attempt to understand the other person's perspective before asserting my own.",
    "I sometimes feel that being too considerate of others only slows down decision-making.",
    "I often find myself mediating conflicts so that everyone involved feels heard.",
    "In competitive situations, I rarely worry about how my actions affect others emotionally.",
    "I tend to assume that most people have reasonable intentions unless proven otherwise.",
    "I am generally skeptical of others' motives until they demonstrate reliability.",
    "I feel uneasy when someone around me is upset, even if the situation does not directly involve me.",
    "I sometimes prioritize personal advantage even when it inconveniences others.",
    "I usually adjust my communication style to maintain harmony in conversations.",
    "I believe blunt honesty is more important than protecting people's feelings.",
    # Extraversion (31-40)
    "Prolonged periods of social interaction tend to energize rather than exhaust me.",
    "In group settings, I often prefer observing quietly rather than actively participating.",
    "I usually find it easy to initiate conversations even with unfamiliar individuals.",
    "After extended social events, I typically feel the need to withdraw and recharge alone.",
    "I often feel stimulated by environments with many people and dynamic activity.",
    "When discussions become lively, I tend to step back rather than insert my opinions.",
    "I am comfortable directing attention toward myself when presenting ideas publicly.",
    "Unexpected social interactions sometimes make me feel mentally drained.",
    "I tend to seek environments where conversations, movement, and interaction are constant.",
    "I usually prefer smaller, quieter settings over crowded or socially demanding ones.",
    # Conscientiousness (41-50)
    "Even when external supervision is absent, I tend to maintain structured progress toward long-term goals.",
    "Deadlines become negotiable in my mind if the task begins to feel tedious or inconvenient.",
    "I often break large responsibilities into organized steps before beginning the task.",
    "I frequently underestimate how much preparation a task will require.",
    "Completing obligations tends to provide me with a stronger sense of satisfaction than spontaneous leisure.",
    "I sometimes leave projects partially completed when my interest shifts elsewhere.",
    "I naturally monitor my progress when working toward objectives to ensure efficiency.",
    "My workspace or digital environment often becomes disorganized without me noticing immediately.",
    "I am inclined to think ahead about possible complications before initiating important tasks.",
    "I rarely develop structured routines unless someone else expects them from me.",
]


def seed_big5_questions():
    db = SessionLocal()

    # Clear existing big5 questions
    b5_ids = db.query(models.Question.id).filter(models.Question.category == "big5")
    db.query(models.Response).filter(
        models.Response.question_id.in_(b5_ids)
    ).delete(synchronize_session=False)
    deleted = db.query(models.Question).filter(
        models.Question.category == "big5"
    ).delete(synchronize_session=False)
    if deleted > 0:
        print(f"Cleared {deleted} existing Big 5 questions.")

    print(f"Seeding {len(QUESTIONS_TEXT)} Big 5 questions...")

    for text in QUESTIONS_TEXT:
        q = models.Question(
            category="big5",
            subtest=None,
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
    print("Big 5 seeding complete.")
    db.close()


if __name__ == "__main__":
    seed_big5_questions()
