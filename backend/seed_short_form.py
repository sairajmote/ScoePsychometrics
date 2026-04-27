"""
seed_short_form.py
Seeds exactly 138 short-form questions that cover every attribute at least once.

Allocation (138 total):
  Big Five      → 19 q  (3-4 per trait)             category: big5
  Enneagram     → 32 q  (3-4 per type)              category: enneagram
  Brain Dom.    → 10 q  (5L + 5R)                   category: brain_dominance
  Temperament   → 19 q  (EI: 10, N: 8, LIE: 1)      category: temperament
  MBTI          → 30 q  (7-8 per dichotomy)         category: mbti
  Multi. Intel. → 28 q  (3-4 per intelligence)      category: multiple_intelligence
  ──────────────────────────────────────────────────────
  TOTAL         → 138 ✓

All questions are drawn verbatim from the existing seed files.
The short form is stored with category = "short_form" and a `subtest`
field that mirrors the full-battery subtest system, so the same scoring
functions can be reused.

Run from project root:
    (.venv) PS Z:\\projects\\Psycho\\psycho_one> python backend/seed_short_form.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend import models


# ─────────────────────────────────────────────────────────────────────────────
# QUESTION POOL
# Each entry: (text, subtest, keyed, correct_answer, opt_a, opt_b, opt_c, opt_d, opt_e, opt_f, opt_g)
# correct_answer is None for Likert items, a letter for dichotomous (temperament).
# opt_f / opt_g are None unless MBTI 7-point scale.
# ─────────────────────────────────────────────────────────────────────────────

LIKERT_5 = ("Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree")
LIKERT_7 = ("Strongly Disagree", "Disagree", "Somewhat Disagree", "Neutral", "Somewhat Agree", "Agree", "Strongly Agree")
YES_NO   = ("Yes", "Maybe", "No", "", None)       # opt_d = "" (NOT NULL), opt_e = None


def q5(text, subtest, keyed):
    """5-point Likert helper."""
    return (text, subtest, keyed, None, *LIKERT_5, None, None)


def q7(text, subtest, keyed):
    """7-point MBTI Likert helper."""
    return (text, subtest, keyed, None, *LIKERT_7)


def qt(text, subtest, keyed, correct_answer):
    """Temperament Yes/Maybe/No helper."""
    return (text, subtest, keyed, correct_answer, "Yes", "Maybe", "No", "", None, None, None)


# ─────────────────────────────────────────────────────────────────────────────
# 1. BIG FIVE — 19 questions  (3-4 per trait, balanced +/-)
#    Source: seed_big5.py
# ─────────────────────────────────────────────────────────────────────────────
BIG5 = [
    # Openness (4 items: 2+, 2-)
    q5("When confronted with unfamiliar perspectives that challenge long-held beliefs, I feel intellectually energized rather than defensive.", "openness", "+"),
    q5("I rarely see value in exploring ideas that have no immediate practical application.", "openness", "-"),
    q5("I am naturally inclined to reinterpret everyday experiences through creative or symbolic meanings.", "openness", "+"),
    q5("I prefer sticking to traditional ways rather than trying something new.", "openness", "-"),

    # Neuroticism (4 items: 2+, 2-)
    q5("Minor setbacks can remain on my mind long after the situation has passed.", "neuroticism", "+"),
    q5("I rarely dwell on stressful situations once they are resolved.", "neuroticism", "-"),
    q5("I sometimes anticipate negative outcomes even when circumstances appear stable.", "neuroticism", "+"),
    q5("I usually recover quickly from embarrassment or mistakes.", "neuroticism", "-"),

    # Agreeableness (4 items: 2+, 2-)
    q5("When disagreements arise, I instinctively attempt to understand the other person's perspective before asserting my own.", "agreeableness", "+"),
    q5("In competitive situations, I rarely worry about how my actions affect others emotionally.", "agreeableness", "-"),
    q5("I feel satisfied when I help others solve their problems.", "agreeableness", "+"),
    q5("I rarely compromise when I strongly believe I am right.", "agreeableness", "-"),

    # Extraversion (4 items: 2+, 2-)
    q5("Prolonged periods of social interaction tend to energize rather than exhaust me.", "extraversion", "+"),
    q5("After extended social events, I typically feel the need to withdraw and recharge alone.", "extraversion", "-"),
    q5("I enjoy expressing my thoughts openly in discussions.", "extraversion", "+"),
    q5("I prefer spending time alone rather than socializing frequently.", "extraversion", "-"),

    # Conscientiousness (3 items: 2+, 1-)
    q5("Even when external supervision is absent, I tend to maintain structured progress toward long-term goals.", "conscientiousness", "+"),
    q5("I often break large responsibilities into organized steps before beginning the task.", "conscientiousness", "+"),
    q5("I sometimes leave projects partially completed when my interest shifts elsewhere.", "conscientiousness", "-"),
]  # Total: 19


# ─────────────────────────────────────────────────────────────────────────────
# 2. ENNEAGRAM — 32 questions  (3-4 per type, all keyed "+")
#    Source: seed_enneagram.py
# ─────────────────────────────────────────────────────────────────────────────
ENNEAGRAM = [
    # Type 1 – Perfectionist (4 items)
    q5("Critical of myself (my own worst critic) and find it easy to be judgmental and critical of other people as well.", "E1", "+"),
    q5("Motivated by the need to be correct, fair, and self-disciplined.", "E1", "+"),
    q5("Have a strong sense of right and wrong and strive for perfection.", "E1", "+"),
    q5("Personal integrity is extremely important to me.", "E1", "+"),

    # Type 2 – Helper (3 items)
    q5("Have a strong need to be noticed, liked, and appreciated for what I do for others.", "E2", "+"),
    q5("I often sense what others need before they ask for it.", "E2", "+"),
    q5("I find it hard to say no when someone asks for my help.", "E2", "+"),

    # Type 3 – Achiever (4 items)
    q5("Work hard and know how to get things done.", "E3", "+"),
    q5("Value exceeding standards and rising to the top of my profession.", "E3", "+"),
    q5("I measure my self-worth largely by my achievements and accomplishments.", "E3", "+"),
    q5("Failure is something I find very difficult to accept about myself.", "E3", "+"),

    # Type 4 – Individualist (3 items)
    q5("Creative and have an artistic view of life.", "E4", "+"),
    q5("Feel different from others, as if \"on the outside looking in.\"", "E4", "+"),
    q5("Feel that something is missing in my life.", "E4", "+"),

    # Type 5 – Investigator (4 items)
    q5("Tend to be more logical than emotional.", "E5", "+"),
    q5("Enjoy spending time alone pursuing my personal interests.", "E5", "+"),
    q5("I prefer to observe a situation thoroughly before deciding to participate.", "E5", "+"),
    q5("I value knowledge and often research topics extensively before forming an opinion.", "E5", "+"),

    # Type 6 – Loyalist (3 items)
    q5("I'm not gullible; you must earn my trust, and I will challenge your loyalty.", "E6", "+"),
    q5("Look for danger, unsafe people, or unsafe situations.", "E6", "+"),
    q5("Making decisions on my own may cause me anxiety.", "E6", "+"),

    # Type 7 – Enthusiast (4 items)
    q5("Like to leave my options open; \"don't hem me in\" describes me well.", "E7", "+"),
    q5("Enjoy trying many things and can do many different things fairly well.", "E7", "+"),
    q5("I get bored easily and constantly look for the next exciting thing to do.", "E7", "+"),
    q5("I find it hard to commit to one path because I fear missing out on other options.", "E7", "+"),

    # Type 8 – Challenger (3 items)
    q5("Love to be challenged and enjoy a good fight.", "E8", "+"),
    q5("Proud about being direct, telling it \"like it is,\" and expressing \"tough love.\"", "E8", "+"),
    q5("I naturally take charge in situations where others seem hesitant or weak.", "E8", "+"),

    # Type 9 – Peacemaker (4 items)
    q5("In relationships, I seek harmony and peace through a sense of belonging and/or by bonding with the other person.", "E9", "+"),
    q5("Try to avoid confrontations.", "E9", "+"),
    q5("Tend to go along with what people say just to get them off my back.", "E9", "+"),
    q5("Dislike confrontation and try to keep the peace.", "E9", "+"),
]  # Total: 32


# ─────────────────────────────────────────────────────────────────────────────
# 3. BRAIN DOMINANCE — 10 questions  (5L + 5R)
#    Source: seed_brain_dominance.py
# ─────────────────────────────────────────────────────────────────────────────
BRAIN_DOMINANCE = [
    # Left-brain (L)
    q5("When faced with a problem, I rely on logic and reasoning above everything else.", "L", "L"),
    q5("I believe that important decisions should always be grounded in facts and logical reasoning.", "L", "L"),
    q5("I plan my life carefully and approach things in a logical, methodical way.", "L", "L"),
    q5("I make decisions based on hard facts and evidence, not on how I feel at the time.", "L", "L"),
    q5("I prefer to work with numbers, data, and concrete information.", "L", "L"),

    # Right-brain (R)
    q5("I have a vivid imagination and spend a lot of time in my own inner world.", "R", "R"),
    q5("I tend to follow my intuition rather than thinking things through step by step.", "R", "R"),
    q5("I would describe myself as a creative person who needs a regular creative outlet.", "R", "R"),
    q5("I enjoy abstract art and am drawn to things that are open to interpretation.", "R", "R"),
    q5("I consider myself a romantic person who is deeply in touch with my emotions.", "R", "R"),
]  # Total: 10


# ─────────────────────────────────────────────────────────────────────────────
# 4. TEMPERAMENT — 19 questions  (Yes/Maybe/No format)
#    Source: seed_temperament.py — choose highest face-validity items
#    EI_temperament: 10, N_temperament: 8, LIE_temperament: 1
# ─────────────────────────────────────────────────────────────────────────────
TEMPERAMENT = [
    # EI_temperament (10 items — balanced Yes=E and No=E)
    qt("Do you often feel a craving for new experiences, to shake things up, or to feel a thrill?",         "EI_temperament", "+", "A"),   # Q1 Yes→e
    qt("Do you consider yourself a carefree person?",                                                        "EI_temperament", "+", "A"),   # Q3 Yes→e
    qt("Do you usually speak and act quickly?",                                                              "EI_temperament", "+", "A"),   # Q8 Yes→e
    qt("Is it true that you could dare to do anything on a dare?",                                           "EI_temperament", "+", "A"),   # Q10 Yes→e
    qt("Does it often happen that you act without thinking, on impulse?",                                    "EI_temperament", "+", "A"),   # Q13 Yes→e
    qt("Do you like going out and being in company often?",                                                  "EI_temperament", "+", "A"),   # Q17 Yes→e
    qt("Do you prefer reading books over meeting people?",                                                   "EI_temperament", "+", "C"),   # Q15 No→e  (introversion)
    qt("Do you try to keep your social circle small, limited to your closest friends?",                      "EI_temperament", "+", "C"),   # Q20 No→e
    qt("Is it true that you love to talk so much that you never miss a chance to chat with a new person?",  "EI_temperament", "+", "A"),   # Q44 Yes→e
    qt("Would you call yourself a self-confident person?",                                                   "EI_temperament", "+", "A"),   # Q49 Yes→e

    # N_temperament (8 items)
    qt("Do you often need friends who can understand you, encourage you, or sympathize with you?",           "N_temperament",  "+", "A"),   # Q2 Yes→l
    qt("Do you often have mood swings — highs and lows?",                                                    "N_temperament",  "+", "A"),   # Q7 Yes→l
    qt("Have you ever felt unhappy without any real reason for it?",                                         "N_temperament",  "+", "A"),   # Q9 Yes→l
    qt("Do you often worry about things you feel you shouldn't have done or said?",                          "N_temperament",  "+", "A"),   # Q14 Yes→l
    qt("Does it ever happen that you can't sleep because different thoughts keep running through your head?","N_temperament",  "+", "A"),   # Q31 Yes→l
    qt("Do you often have nightmares?",                                                                      "N_temperament",  "+", "A"),   # Q43 Yes→l
    qt("Are you easily hurt by criticism of your faults or your work?",                                     "N_temperament",  "+", "A"),   # Q50 Yes→l
    qt("Do you suffer from insomnia?",                                                                       "N_temperament",  "+", "A"),   # Q57 Yes→l

    # LIE_temperament (1 item — validity check)
    qt("Do you always keep your promises, even when it's inconvenient for you?",                             "LIE_temperament","+", "A"),   # Q6 Yes→n (lie scale)
]  # Total: 19


# ─────────────────────────────────────────────────────────────────────────────
# 5. MBTI — 30 questions  (7-8 per dichotomy; balanced poles)
#    Source: seed_mbti.py  (7-point Likert scale: A–G)
# ─────────────────────────────────────────────────────────────────────────────
MBTI = [
    # EI — 8 items (4E + 4I)
    q7("I feel energized when I spend time with a lot of people.", "EI", "+"),          # E-pole
    q7("I enjoy being the center of attention.", "EI", "+"),                            # E-pole
    q7("I seek out social events and gatherings.", "EI", "+"),                          # E-pole
    q7("I like to talk through my problems.", "EI", "+"),                               # E-pole
    q7("I prefer to reflect quietly by myself.", "EI", "-"),                            # I-pole
    q7("I often think before I speak.", "EI", "-"),                                     # I-pole
    q7("I need time alone to recharge after social interactions.", "EI", "-"),          # I-pole
    q7("I tend to keep my thoughts and feelings to myself.", "EI", "-"),               # I-pole

    # SN — 8 items (4S + 4N)
    q7("I focus on details and specifics when learning something new.", "SN", "+"),     # S-pole
    q7("I rely on my experiences when making decisions.", "SN", "+"),                   # S-pole
    q7("I prefer clear and concrete information over abstract ideas.", "SN", "+"),      # S-pole
    q7("I am practical and down-to-earth.", "SN", "+"),                                 # S-pole
    q7("I enjoy thinking about the future and the possibilities it holds.", "SN", "-"), # N-pole
    q7("I trust my gut feelings and intuition.", "SN", "-"),                            # N-pole
    q7("I often get lost in my own imagination.", "SN", "-"),                           # N-pole
    q7("I often contemplate the meaning and purpose of life.", "SN", "-"),             # N-pole

    # TF — 7 items (4T + 3F)
    q7("I prioritize logic and objectivity when making decisions.", "TF", "+"),         # T-pole
    q7("I value fairness and justice.", "TF", "+"),                                     # T-pole
    q7("I am more likely to criticize than to compliment.", "TF", "+"),                 # T-pole
    q7("I enjoy analyzing problems and finding logical solutions.", "TF", "+"),         # T-pole
    q7("I find it easy to relate to people and understand their perspective.", "TF", "-"), # F-pole
    q7("I consider people's feelings when making decisions.", "TF", "-"),               # F-pole
    q7("I am concerned with maintaining harmony in my relationships.", "TF", "-"),     # F-pole

    # JP — 7 items (4J + 3P)
    q7("I prefer to have a plan and stick to it.", "JP", "+"),                          # J-pole
    q7("I like to complete tasks well before the deadline.", "JP", "+"),                # J-pole
    q7("I like to keep my space organized and tidy.", "JP", "+"),                       # J-pole
    q7("I set goals and work systematically towards them.", "JP", "+"),                 # J-pole
    q7("I am comfortable with changes and surprises.", "JP", "-"),                      # P-pole
    q7("I often leave tasks until the last minute.", "JP", "-"),                        # P-pole
    q7("I prefer to keep my options open.", "JP", "-"),                                # P-pole
]  # Total: 30


# ─────────────────────────────────────────────────────────────────────────────
# 6. MULTIPLE INTELLIGENCE — 28 questions  (3-4 per intelligence × 9)
#    Source: seed_multiple_intelligence.py (all positively keyed)
# ─────────────────────────────────────────────────────────────────────────────
MULTIPLE_INTELLIGENCE = [
    # Linguistic (3 items)
    q5("I enjoy learning new words and/or languages.", "LI", "+"),
    q5("I am interested in writing poetry, quotes, stories, or journals.", "LI", "+"),
    q5("I love reading.", "LI", "+"),

    # Logical-Mathematical (3 items)
    q5("I enjoy sequential puzzles like Rubik's cube or Sudoku.", "LMI", "+"),
    q5("I am good with numbers.", "LMI", "+"),
    q5("I enjoy challenges that require lateral thinking, like chess.", "LMI", "+"),

    # Musical (3 items)
    q5("I enjoy singing or playing a musical instrument.", "MI", "+"),
    q5("I am always discovering new kinds of music.", "MI", "+"),
    q5("I can tell when a note is off-key.", "MI", "+"),

    # Bodily-Kinesthetic (3 items)
    q5("I like dancing, sports, or working out.", "BKI", "+"),
    q5("I am interested in sports.", "BKI", "+"),
    q5("I like sewing, carving, model-building, or other activities that involve dexterity.", "BKI", "+"),

    # Spatial-Visual (3 items)
    q5("I am good at reading maps and finding my way around unfamiliar places.", "SVI", "+"),
    q5("I am better at remembering faces than names.", "SVI", "+"),
    q5("I enjoy activities like drawing, sketching, or doodling.", "SVI", "+"),

    # Interpersonal (3 items)
    q5("Others often come to me for support or advice.", "IPI", "+"),
    q5("I am good at mediating disputes or conflicts between individuals.", "IPI", "+"),
    q5("I am good at reading people's moods and adjusting how I interact with them.", "IPI", "+"),

    # Intrapersonal (3 items)
    q5("I like to spend time going deeper and deeper into the things that are going on within me.", "INPI", "+"),
    q5("I enjoy spending time alone, processing my own emotions and reactions to things.", "INPI", "+"),
    q5("I regularly set personal goals and reflect on my progress.", "INPI", "+"),

    # Naturalistic (3 items)
    q5("I like tending to gardens and plants.", "NI", "+"),
    q5("I feel the most alive when I am in contact with nature.", "NI", "+"),
    q5("I enjoy learning about different species of plants and animals.", "NI", "+"),

    # Existential (4 items)
    q5("I often contemplate questions related to theology or philosophy.", "EI", "+"),
    q5("I am often pondering the meaning of life.", "EI", "+"),
    q5("I keep going over deep questions about life and existence that seem foolish to others.", "EI", "+"),
    q5("I often reflect on whether my daily actions align with a deeper sense of purpose.", "EI", "+"),
]  # Total: 28




# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLE FULL 150-QUESTION LIST
# ─────────────────────────────────────────────────────────────────────────────
ALL_QUESTIONS = (
    BIG5               # 19
    + ENNEAGRAM          # 32
    + BRAIN_DOMINANCE    # 10
    + TEMPERAMENT        # 19
    + MBTI               # 30
    + MULTIPLE_INTELLIGENCE  # 28
)

assert len(ALL_QUESTIONS) == 138, (
    f"Expected 138 questions, got {len(ALL_QUESTIONS)}. Check section counts."
)

_SECTION_LABELS = {
    "openness":              "big5",
    "neuroticism":           "big5",
    "agreeableness":         "big5",
    "extraversion":          "big5",
    "conscientiousness":     "big5",
    "E1": "enneagram", "E2": "enneagram", "E3": "enneagram",
    "E4": "enneagram", "E5": "enneagram", "E6": "enneagram",
    "E7": "enneagram", "E8": "enneagram", "E9": "enneagram",
    "L":  "brain_dominance",
    "R":  "brain_dominance",
    "EI_temperament":   "temperament",
    "N_temperament":    "temperament",
    "LIE_temperament":  "temperament",
    "EI": "mbti",
    "SN": "mbti",
    "TF": "mbti",
    "JP": "mbti",
    "LI": "multiple_intelligence",
    "LMI": "multiple_intelligence",
    "MI":  "multiple_intelligence",
    "BKI": "multiple_intelligence",
    "SVI": "multiple_intelligence",
    "IPI": "multiple_intelligence",
    "INPI": "multiple_intelligence",
    "NI":  "multiple_intelligence",
}


def _category_for(subtest: str) -> str:
    """Derive the category tag from the subtest key."""
    return _SECTION_LABELS.get(subtest, "short_form")


def seed_short_form():
    db = SessionLocal()

    # Clear any existing short_form questions
    sf_ids = db.query(models.Question.id).filter(models.Question.category == "short_form")
    db.query(models.Response).filter(
        models.Response.question_id.in_(sf_ids)
    ).delete(synchronize_session=False)
    deleted = db.query(models.Question).filter(
        models.Question.category == "short_form"
    ).delete(synchronize_session=False)
    if deleted > 0:
        print(f"Cleared {deleted} existing short-form questions.")

    print(f"Seeding {len(ALL_QUESTIONS)} short-form questions...")

    for i, entry in enumerate(ALL_QUESTIONS, start=1):
        text, subtest, keyed, correct_answer, opt_a, opt_b, opt_c, opt_d, opt_e, opt_f, opt_g = entry

        q = models.Question(
            category="short_form",
            subtest=subtest,
            text=text,
            option_a=opt_a,
            option_b=opt_b,
            option_c=opt_c,
            option_d=opt_d,
            option_e=opt_e,
            option_f=opt_f,
            option_g=opt_g,
            keyed=keyed,
            correct_answer=correct_answer,
        )
        db.add(q)

    db.commit()
    print("Short-form seeding complete.")
    db.close()

    # ── Print a quick summary ──────────────────────────────────────────────
    from collections import Counter
    counts = Counter(_category_for(e[1]) for e in ALL_QUESTIONS)
    print("\nQuestion count by subtest:")
    for cat, n in sorted(counts.items()):
        print(f"  {cat:<30} {n}")
    print(f"  {'TOTAL':<30} {sum(counts.values())}")


if __name__ == "__main__":
    seed_short_form()
