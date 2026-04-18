"""
scoring_temperament.py
Scores the 57-item Eysenck Temperament questionnaire.

Dimensions
----------
  EI_temperament  →  Extraversion (E)
  N_temperament   →  Neuroticism  (N)
  LIE_temperament →  Lie scale    (validity check)

Classification grid (Eysenck)
------------------------------
  High E  +  Low N   →  Sanguine
  High E  +  High N  →  Choleric
  Low E   +  Low N   →  Phlegmatic
  Low E   +  High N  →  Melancholic

Threshold: midpoint of each dimension's maximum possible score.
  E max  = 23 questions  →  threshold = 12
  N max  = 30 questions  →  threshold = 15
"""

from typing import List, Dict, Any


# Maximum scores per dimension (derived from the grading key)
E_MAX = 23   # number of EI_temperament questions
N_MAX = 30   # number of N_temperament questions

# Midpoint thresholds (≥ threshold = High, < threshold = Low)
E_THRESHOLD = 12
N_THRESHOLD = 15


def score_temperament(scoring_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parameters
    ----------
    scoring_data : list of dicts, each with keys:
        subtest        : "EI_temperament" | "N_temperament" | "LIE_temperament" | None
        correct_answer : "A" | "C" | None   (the answer that earns a point)
        selected_option: "A" | "B" | "C"    (what the candidate actually chose)

    Returns
    -------
    dict with:
        e_score, n_score, lie_score
        e_max, n_max
        temperament_type : "Sanguine" | "Choleric" | "Phlegmatic" | "Melancholic"
        description      : short string description
        high_e, high_n   : bool
    """
    e_score   = 0
    n_score   = 0
    lie_score = 0

    for item in scoring_data:
        subtest        = item.get("subtest")
        correct_answer = item.get("correct_answer")   # "A" / "C" / None
        selected       = item.get("selected_option")  # "A" / "B" / "C"

        # No points for this question (e.g. Q34)
        if not subtest or not correct_answer:
            continue

        if selected == correct_answer:
            if subtest == "EI_temperament":
                e_score += 1
            elif subtest == "N_temperament":
                n_score += 1
            elif subtest == "LIE_temperament":
                lie_score += 1

    high_e = e_score >= E_THRESHOLD
    high_n = n_score >= N_THRESHOLD

    if high_e and not high_n:
        temperament_type = "Sanguine"
        description = "Sanguine individuals are lively, outgoing, and full of energy. They enjoy social interactions, easily connect with others, and often bring enthusiasm and positivity into any environment. They tend to be expressive, spontaneous, and fun-loving, making them great at building relationships. However, their high energy can sometimes lead to impulsiveness, lack of focus, and difficulty sticking to long-term commitments. They thrive in dynamic environments where creativity, communication, and interaction are encouraged."
    elif high_e and high_n:
        temperament_type = "Choleric"
        description = "Choleric individuals are strong-willed, ambitious, and highly goal-driven. They naturally take on leadership roles and are confident in making decisions, especially in challenging situations. Their determination and focus help them achieve results efficiently. However, they may come across as dominant, impatient, or overly controlling when things don’t go according to plan. They prefer structure, control, and clear objectives, and they excel in environments that require leadership, strategy, and quick decision-making."
    elif not high_e and not high_n:
        temperament_type = "Phlegmatic"
        description = "Phlegmatic individuals are calm, patient, and easygoing. They prefer a peaceful and stable environment and are known for their reliability and supportive nature. They are good listeners, loyal friends, and excellent team players who help maintain harmony in groups. However, they may avoid conflict, resist change, and sometimes lack urgency or motivation in decision-making. They perform well in environments that value consistency, cooperation, and long-term stability."
    else:  # Low E + High N
        temperament_type = "Melancholic"
        description = "Melancholic individuals are thoughtful, analytical, and deeply introspective. They value organization, detail, and precision, often striving for perfection in their work. They tend to be creative and emotionally aware, making them highly empathetic and reflective. However, they may struggle with overthinking, self-criticism, and sensitivity to criticism from others. They thrive in structured environments where they can plan, analyze, and express their creativity in meaningful and purposeful ways."

    return {
        "temperament_type": temperament_type,
        "description": description,
        "e_score": e_score,
        "n_score": n_score,
        "lie_score": lie_score,
        "e_max": E_MAX,
        "n_max": N_MAX,
        "high_e": high_e,
        "high_n": high_n,
    }
