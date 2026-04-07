"""
seed_big5.py
Seeds 100 Big 5 Personality questions using a 5-point Likert scale.
Scale: Strongly Disagree / Disagree / Neutral / Agree / Strongly Agree

Scoring keys per big5.txt:
  O (Openness)        — Questions 1–20
  N (Neuroticism)     — Questions 21–40
  A (Agreeableness)   — Questions 41–60
  E (Extraversion)    — Questions 61–80
  C (Conscientiousness) — Questions 81–100
  + = positively keyed (agree = higher trait score)
  - = negatively keyed (agree = lower trait score, reverse-scored)

Run from the project root with the virtual environment active:
    (.venv) PS Z:\\projects\\Psycho\\psycho_one> python backend/seed_big5.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend import models


# (text, subtest, keyed) — ordered exactly as in big5.txt
QUESTIONS = [
    # Openness to Experience (1-10)
    ("When confronted with unfamiliar perspectives that challenge long-held beliefs, I feel intellectually energized rather than defensive.", "openness", "+"),
    ("I rarely see value in exploring ideas that have no immediate practical application.", "openness", "-"),
    ("Abstract discussions about philosophy, art, or theoretical possibilities tend to capture my attention more than routine conversations.", "openness", "+"),
    ("I prefer familiar patterns of thinking over experimenting with unconventional viewpoints.", "openness", "-"),
    ("Encountering ambiguous or complex problems usually stimulates curiosity in me rather than frustration.", "openness", "+"),
    ("I feel uncomfortable when conversations drift into imaginative or speculative territories.", "openness", "-"),
    ("I am naturally inclined to reinterpret everyday experiences through creative or symbolic meanings.", "openness", "+"),
    ("Novel experiences often seem unnecessarily disruptive to an otherwise efficient routine.", "openness", "-"),
    ("I frequently find myself mentally exploring 'what if' scenarios beyond immediate reality.", "openness", "+"),
    ("I see little benefit in questioning traditions or long-standing methods that already function adequately.", "openness", "-"),
    # Neuroticism (11-20)
    ("Minor setbacks can remain on my mind long after the situation has passed.", "neuroticism", "+"),
    ("I rarely dwell on stressful situations once they are resolved.", "neuroticism", "-"),
    ("Unexpected uncertainty tends to trigger noticeable tension in my thoughts.", "neuroticism", "+"),
    ("Emotional fluctuations rarely influence how I approach daily responsibilities.", "neuroticism", "-"),
    ("I sometimes anticipate negative outcomes even when circumstances appear stable.", "neuroticism", "+"),
    ("I generally remain calm even when several problems arise simultaneously.", "neuroticism", "-"),
    ("Criticism can linger in my mind longer than compliments.", "neuroticism", "+"),
    ("I usually recover quickly from embarrassment or mistakes.", "neuroticism", "-"),
    ("Situations outside my control occasionally provoke persistent worry.", "neuroticism", "+"),
    ("I tend to maintain emotional steadiness even during demanding periods.", "neuroticism", "-"),
    # Agreeableness (21-30)
    ("When disagreements arise, I instinctively attempt to understand the other person's perspective before asserting my own.", "agreeableness", "+"),
    ("I sometimes feel that being too considerate of others only slows down decision-making.", "agreeableness", "-"),
    ("I often find myself mediating conflicts so that everyone involved feels heard.", "agreeableness", "+"),
    ("In competitive situations, I rarely worry about how my actions affect others emotionally.", "agreeableness", "-"),
    ("I tend to assume that most people have reasonable intentions unless proven otherwise.", "agreeableness", "+"),
    ("I am generally skeptical of others' motives until they demonstrate reliability.", "agreeableness", "-"),
    ("I feel uneasy when someone around me is upset, even if the situation does not directly involve me.", "agreeableness", "+"),
    ("I sometimes prioritize personal advantage even when it inconveniences others.", "agreeableness", "-"),
    ("I usually adjust my communication style to maintain harmony in conversations.", "agreeableness", "+"),
    ("I believe blunt honesty is more important than protecting people's feelings.", "agreeableness", "-"),
    # Extraversion (31-40)
    ("Prolonged periods of social interaction tend to energize rather than exhaust me.", "extraversion", "+"),
    ("In group settings, I often prefer observing quietly rather than actively participating.", "extraversion", "-"),
    ("I usually find it easy to initiate conversations even with unfamiliar individuals.", "extraversion", "+"),
    ("After extended social events, I typically feel the need to withdraw and recharge alone.", "extraversion", "-"),
    ("I often feel stimulated by environments with many people and dynamic activity.", "extraversion", "+"),
    ("When discussions become lively, I tend to step back rather than insert my opinions.", "extraversion", "-"),
    ("I am comfortable directing attention toward myself when presenting ideas publicly.", "extraversion", "+"),
    ("Unexpected social interactions sometimes make me feel mentally drained.", "extraversion", "-"),
    ("I tend to seek environments where conversations, movement, and interaction are constant.", "extraversion", "+"),
    ("I usually prefer smaller, quieter settings over crowded or socially demanding ones.", "extraversion", "-"),
    # Conscientiousness (41-50)
    ("Even when external supervision is absent, I tend to maintain structured progress toward long-term goals.", "conscientiousness", "+"),
    ("Deadlines become negotiable in my mind if the task begins to feel tedious or inconvenient.", "conscientiousness", "-"),
    ("I often break large responsibilities into organized steps before beginning the task.", "conscientiousness", "+"),
    ("I frequently underestimate how much preparation a task will require.", "conscientiousness", "-"),
    ("Completing obligations tends to provide me with a stronger sense of satisfaction than spontaneous leisure.", "conscientiousness", "+"),
    ("I sometimes leave projects partially completed when my interest shifts elsewhere.", "conscientiousness", "-"),
    ("I naturally monitor my progress when working toward objectives to ensure efficiency.", "conscientiousness", "+"),
    ("My workspace or digital environment often becomes disorganized without me noticing immediately.", "conscientiousness", "-"),
    ("I am inclined to think ahead about possible complications before initiating important tasks.", "conscientiousness", "+"),
    ("I rarely develop structured routines unless someone else expects them from me.", "conscientiousness", "-"),
    # Extra Big Five questions — expanded set
    # Openness to Experience (O)
    ("I enjoy experimenting with new approaches even when familiar methods already work well.", "openness", "+"),
    ("I tend to avoid activities that require imaginative thinking.", "openness", "-"),
    ("Learning about unfamiliar cultures or ideas excites me.", "openness", "+"),
    ("I prefer sticking to traditional ways rather than trying something new.", "openness", "-"),
    ("I often reflect deeply on abstract concepts or ideas.", "openness", "+"),
    ("I find creative hobbies unnecessary or unproductive.", "openness", "-"),
    ("I am curious about possibilities beyond what is immediately visible.", "openness", "+"),
    ("I feel uneasy when asked to think outside conventional boundaries.", "openness", "-"),
    ("I enjoy connecting unrelated ideas to form something new.", "openness", "+"),
    ("I believe imagination is less important than practicality.", "openness", "-"),
    # Neuroticism (N)
    ("I sometimes find it difficult to relax even when there is no clear reason to worry.", "neuroticism", "+"),
    ("I remain emotionally stable even under unexpected pressure.", "neuroticism", "-"),
    ("Small problems can feel overwhelming at times.", "neuroticism", "+"),
    ("I usually stay composed even when things don’t go as planned.", "neuroticism", "-"),
    ("I tend to overthink situations that others might ignore.", "neuroticism", "+"),
    ("I can quickly let go of worries once a situation is resolved.", "neuroticism", "-"),
    ("I often feel tense without a clear cause.", "neuroticism", "+"),
    ("I handle criticism without it affecting my mood significantly.", "neuroticism", "-"),
    ("I sometimes imagine worst-case scenarios unnecessarily.", "neuroticism", "+"),
    ("I generally feel confident and secure in my emotions.", "neuroticism", "-"),
    # Agreeableness (A)
    ("I try to be considerate of others even when it requires extra effort.", "agreeableness", "+"),
    ("I prioritize my own needs even if it inconveniences others.", "agreeableness", "-"),
    ("I feel satisfied when I help others solve their problems.", "agreeableness", "+"),
    ("I rarely compromise when I strongly believe I am right.", "agreeableness", "-"),
    ("I value cooperation more than competition.", "agreeableness", "+"),
    ("I sometimes ignore others’ feelings to get things done faster.", "agreeableness", "-"),
    ("I tend to forgive people easily after conflicts.", "agreeableness", "+"),
    ("I find it difficult to trust people without strong proof.", "agreeableness", "-"),
    ("I try to maintain positive relationships with people around me.", "agreeableness", "+"),
    ("I believe personal success matters more than group harmony.", "agreeableness", "-"),
    # Extraversion (E)
    ("I enjoy being the center of attention in social gatherings.", "extraversion", "+"),
    ("I feel uncomfortable speaking up in large groups.", "extraversion", "-"),
    ("I actively seek opportunities to meet new people.", "extraversion", "+"),
    ("I prefer spending time alone rather than socializing frequently.", "extraversion", "-"),
    ("I feel energized when engaging in group activities.", "extraversion", "+"),
    ("I avoid initiating conversations with strangers.", "extraversion", "-"),
    ("I enjoy expressing my thoughts openly in discussions.", "extraversion", "+"),
    ("Social interactions often leave me feeling exhausted.", "extraversion", "-"),
    ("I like environments that are lively and interactive.", "extraversion", "+"),
    ("I tend to stay quiet even when I have something to say.", "extraversion", "-"),
    # Conscientiousness (C)
    ("I set clear goals and work consistently toward achieving them.", "conscientiousness", "+"),
    ("I often delay tasks until the last moment.", "conscientiousness", "-"),
    ("I pay attention to details to ensure accuracy in my work.", "conscientiousness", "+"),
    ("I find it hard to stay organized over long periods.", "conscientiousness", "-"),
    ("I feel responsible for completing tasks on time.", "conscientiousness", "+"),
    ("I sometimes lose focus and leave work unfinished.", "conscientiousness", "-"),
    ("I plan my activities in advance to avoid last-minute stress.", "conscientiousness", "+"),
    ("I struggle to maintain discipline without external pressure.", "conscientiousness", "-"),
    ("I take pride in being reliable and dependable.", "conscientiousness", "+"),
    ("I often act impulsively without proper planning.", "conscientiousness", "-"),
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

    print(f"Seeding {len(QUESTIONS)} Big 5 questions...")

    for text, subtest, keyed in QUESTIONS:
        q = models.Question(
            category="big5",
            subtest=subtest,
            text=text,
            option_a="Strongly Disagree",
            option_b="Disagree",
            option_c="Neutral",
            option_d="Agree",
            option_e="Strongly Agree",
            keyed=keyed,
            correct_answer=None,
        )
        db.add(q)

    db.commit()
    print("Big 5 seeding complete.")
    db.close()


if __name__ == "__main__":
    seed_big5_questions()
