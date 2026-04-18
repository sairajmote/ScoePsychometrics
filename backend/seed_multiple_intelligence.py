"""
seed_multiple_intelligence.py
Seeds 90 Multiple Intelligence questions using a 5-point Likert scale.
Scale: Strongly Disagree / Disagree / Neutral / Agree / Strongly Agree

Scoring keys (stored in the `subtest` column):
  LI   → Linguistic Intelligence           (10 questions: 22, 30, 38, 41, 45, 46, 47, 48, 49, 50)
  LMI  → Logical-Mathematical Intelligence (10 questions: 3, 8, 10, 13, 20, 21, 40, 51, 52, 53)
  MI   → Musical Intelligence              (10 questions: 2, 17, 18, 34, 42, 54, 55, 56, 57, 58)
  BKI  → Bodily-Kinesthetic Intelligence   (10 questions: 6, 16, 26, 31, 44, 59, 60, 61, 62, 63)
  SVI  → Spatial-Visual Intelligence       (10 questions: 12, 19, 33, 64, 65, 66, 67, 68, 69, 70)
  IPI  → Interpersonal Intelligence        (10 questions: 4, 7, 23, 24, 32, 71, 72, 73, 74, 75)
  INPI → Intrapersonal Intelligence        (10 questions: 1, 11, 14, 25, 37, 76, 77, 78, 79, 80)
  NI   → Naturalistic Intelligence         (10 questions: 9, 28, 29, 35, 43, 81, 82, 83, 84, 85)
  EI   → Existential Intelligence          (10 questions: 5, 15, 27, 36, 39, 86, 87, 88, 89, 90)

Run from the project root with the virtual environment active:
    (.venv) PS Z:\\projects\\Psycho\\psycho_one> python backend/seed_multiple_intelligence.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend import models


# Each tuple: (question_text, subtest_key)
# Ordered by the original numbering in multiple_intelligence_extra.txt
QUESTIONS = [
    # 1  [INPI]
    ("I like to spend time going deeper and deeper into the things that are going on within me.", "INPI"),
    # 2  [MI]
    ("I enjoy singing or playing a musical instrument.", "MI"),
    # 3  [LMI]
    ("I enjoy sequential puzzles like Rubik's cube or Sudoku.", "LMI"),
    # 4  [IPI]
    ("Others often come to me for support or advice.", "IPI"),
    # 5  [EI]
    ("I often contemplate questions related to theology or philosophy.", "EI"),
    # 6  [BKI]
    ("I don't mind getting my hands dirty from activities that involve creating, fixing, or building things.", "BKI"),
    # 7  [IPI]
    ("I spend a lot of time thinking about the emotions of others.", "IPI"),
    # 8  [LMI]
    ("I am good with numbers.", "LMI"),
    # 9  [NI]
    ("I like tending to gardens and plants.", "NI"),
    # 10 [LMI]
    ("I like measuring or categorizing stuff.", "LMI"),
    # 11 [INPI]
    ("I enjoy spending time alone, processing my own emotions and reactions to things.", "INPI"),
    # 12 [SVI]
    ("I am good at reading maps and finding my way around unfamiliar places.", "SVI"),
    # 13 [LMI]
    ("I have always excelled in math and science at school.", "LMI"),
    # 14 [INPI]
    ("It is easy for me to identify how I feel and why.", "INPI"),
    # 15 [EI]
    ("I am often pondering the meaning of life.", "EI"),
    # 16 [BKI]
    ("I like dancing, sports, or working out.", "BKI"),
    # 17 [MI]
    ("I am often humming a song or tune to myself in my head.", "MI"),
    # 18 [MI]
    ("Music is one of my biggest interests.", "MI"),
    # 19 [SVI]
    ("I vividly remember details about furniture and the interior decoration of rooms that I've been in.", "SVI"),
    # 20 [LMI]
    ("I can learn better if things are accompanied by charts, diagrams, or other technical illustrations.", "LMI"),
    # 21 [LMI]
    ("I enjoy challenges that require lateral thinking, like chess.", "LMI"),
    # 22 [LI]
    ("I enjoy learning new words and/or languages.", "LI"),
    # 23 [IPI]
    ("I am good at mediating disputes or conflicts between individuals.", "IPI"),
    # 24 [IPI]
    ("I am good at making a good impression when meeting new people.", "IPI"),
    # 25 [INPI]
    ("I spend a lot of time reflecting on my own reactions to things.", "INPI"),
    # 26 [BKI]
    ("I find it easiest to solve problems when my body is in motion.", "BKI"),
    # 27 [EI]
    ("Questions like 'Where is humanity heading?' or 'Why are we here?' are of interest to me.", "EI"),
    # 28 [NI]
    ("I like taking long walks in nature, alone or with my friends.", "NI"),
    # 29 [NI]
    ("I feel the most alive when I am in contact with nature.", "NI"),
    # 30 [LI]
    ("I am interested in writing poetry, quotes, stories, or journals.", "LI"),
    # 31 [BKI]
    ("I am interested in sports.", "BKI"),
    # 32 [IPI]
    ("I am good at detecting dishonesty in others.", "IPI"),
    # 33 [SVI]
    ("I am better at remembering faces than names.", "SVI"),
    # 34 [MI]
    ("I am always discovering new kinds of music.", "MI"),
    # 35 [NI]
    ("I am usually good with animals.", "NI"),
    # 36 [EI]
    ("I keep going over deep questions about life and existence that seem foolish to others.", "EI"),
    # 37 [INPI]
    ("I spend a lot of time analyzing my own emotions and reactions.", "INPI"),
    # 38 [LI]
    ("I often look things up in the dictionary.", "LI"),
    # 39 [EI]
    ("I enjoy learning about how the various world religions have attempted to answer 'the big questions'.", "EI"),
    # 40 [LMI]
    ("I draw charts and tables to help me think.", "LMI"),
    # 41 [LI]
    ("I love reading.", "LI"),
    # 42 [MI]
    ("I can tell when a note is off-key.", "MI"),
    # 43 [NI]
    ("I enjoy learning about different species of plants and animals.", "NI"),
    # 44 [BKI]
    ("I like sewing, carving, model-building, or other activities that involve dexterity.", "BKI"),
    # --- Extra questions from multiple_intelligence_extra.txt ---
    # 45 [LI]
    ("I enjoy debating or discussing ideas through conversation.", "LI"),
    # 46 [LI]
    ("I find it easy to explain complex ideas to others in simple words.", "LI"),
    # 47 [LI]
    ("I tend to remember information better when I write it down.", "LI"),
    # 48 [LI]
    ("I enjoy word games like crosswords, Scrabble, or anagrams.", "LI"),
    # 49 [LI]
    ("I prefer reading instructions rather than having someone show me how to do something.", "LI"),
    # 50 [LI]
    ("I often think in words rather than images or feelings.", "LI"),
    # 51 [LMI]
    ("I enjoy finding patterns or relationships between numbers and concepts.", "LMI"),
    # 52 [LMI]
    ("I like to break problems down into steps before solving them.", "LMI"),
    # 53 [LMI]
    ("I tend to question things and look for logical explanations rather than accepting them at face value.", "LMI"),
    # 54 [MI]
    ("I find it easy to keep rhythm when listening to music.", "MI"),
    # 55 [MI]
    ("I often associate certain songs or melodies with specific memories or emotions.", "MI"),
    # 56 [MI]
    ("I can easily remember and reproduce melodies I have heard only a few times.", "MI"),
    # 57 [MI]
    ("I find background noise or off-beat sounds distracting when trying to concentrate.", "MI"),
    # 58 [MI]
    ("I enjoy learning about music theory, composition, or the history of music.", "MI"),
    # 59 [BKI]
    ("I learn physical skills better by doing them than by reading or watching.", "BKI"),
    # 60 [BKI]
    ("I tend to use hand gestures and body language when I communicate.", "BKI"),
    # 61 [BKI]
    ("I enjoy activities that require physical coordination like yoga, martial arts, or dance.", "BKI"),
    # 62 [BKI]
    ("I find it hard to sit still for long periods of time.", "BKI"),
    # 63 [BKI]
    ("I am good at mimicking the movements or gestures of other people.", "BKI"),
    # 64 [SVI]
    ("I enjoy activities like drawing, sketching, or doodling.", "SVI"),
    # 65 [SVI]
    ("I think in pictures and find it easy to visualize concepts in my mind.", "SVI"),
    # 66 [SVI]
    ("I can easily tell when something is visually out of place or unbalanced.", "SVI"),
    # 67 [SVI]
    ("I enjoy puzzles that involve shapes, patterns, or spatial reasoning.", "SVI"),
    # 68 [SVI]
    ("I have a good sense of direction and rarely get lost.", "SVI"),
    # 69 [SVI]
    ("I prefer diagrams and visual aids over written or verbal explanations.", "SVI"),
    # 70 [SVI]
    ("I notice details in my surroundings that others often overlook.", "SVI"),
    # 71 [IPI]
    ("I am good at reading people's moods and adjusting how I interact with them.", "IPI"),
    # 72 [IPI]
    ("I enjoy working in teams more than working alone.", "IPI"),
    # 73 [IPI]
    ("I find it easy to motivate and inspire other people.", "IPI"),
    # 74 [IPI]
    ("I tend to be the person in a group who keeps everyone connected.", "IPI"),
    # 75 [IPI]
    ("I enjoy meeting new people and learning about their lives and experiences.", "IPI"),
    # 76 [INPI]
    ("I am aware of how my moods affect the people around me.", "INPI"),
    # 77 [INPI]
    ("I regularly set personal goals and reflect on my progress.", "INPI"),
    # 78 [INPI]
    ("I prefer to work independently and at my own pace.", "INPI"),
    # 79 [INPI]
    ("I am clear about my personal values and what matters most to me in life.", "INPI"),
    # 80 [INPI]
    ("I find journaling or self-reflection to be a useful and meaningful activity.", "INPI"),
    # 81 [NI]
    ("I notice changes in weather, seasons, or the natural environment easily.", "NI"),
    # 82 [NI]
    ("I enjoy outdoor activities like hiking, camping, or exploring nature.", "NI"),
    # 83 [NI]
    ("I find it easy to identify different types of birds, trees, or plants.", "NI"),
    # 84 [NI]
    ("I feel more calm and restored after spending time outdoors.", "NI"),
    # 85 [NI]
    ("I am drawn to documentaries or books about wildlife, nature, or the environment.", "NI"),
    # 86 [EI]
    ("I often think about what happens after death and what it means for how we live.", "EI"),
    # 87 [EI]
    ("I am deeply curious about the origins of the universe and humanity's place in it.", "EI"),
    # 88 [EI]
    ("I find conversations about the purpose and meaning of life energizing rather than exhausting.", "EI"),
    # 89 [EI]
    ("I am drawn to philosophy, ethics, or spiritual traditions that seek to explain existence.", "EI"),
    # 90 [EI]
    ("I often reflect on whether my daily actions align with a deeper sense of purpose.", "EI"),
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

    print(f"Seeding {len(QUESTIONS)} Multiple Intelligence questions...")

    for text, subtest in QUESTIONS:
        q = models.Question(
            category="multiple_intelligence",
            subtest=subtest,
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
