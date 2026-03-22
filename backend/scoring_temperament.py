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
        description = "Sociable, outgoing, optimistic, and easygoing."
    elif high_e and high_n:
        temperament_type = "Choleric"
        description = "Driven, energetic, ambitious, and quick to react."
    elif not high_e and not high_n:
        temperament_type = "Phlegmatic"
        description = "Calm, reliable, peaceful, and consistent."
    else:  # Low E + High N
        temperament_type = "Melancholic"
        description = "Analytical, thoughtful, detail-oriented, and deep-feeling."

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
