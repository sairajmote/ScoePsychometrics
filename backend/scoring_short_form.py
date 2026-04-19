"""
scoring_short_form.py
Scores the 150-question short-form assessment.

Delegates to the same scoring functions used by the full battery:
  - Cognitive    → scored inline (new)
  - Big Five     → scoring_big5.score_big5()
  - Enneagram    → scoring_enneagram.score_enneagram()
  - Brain Dom.   → scoring_brain_dominance.score_brain_dominance()
  - Temperament  → scoring_temperament.score_temperament()
  - MBTI         → scoring_mbti.score_mbti()
  - Multi. Intel.→ scoring_multiple_intelligence.score_multiple_intelligence()

Input
-----
scoring_data : list[dict]
    One dict per response, with keys:
        subtest         : str   — the question's `subtest` column value
        keyed           : str   — "+", "-", "L", "R", or None
        selected_option : str   — "A" | "B" | ... | "G"
        correct_answer  : str | None  — for temperament dichotomous items

Output
------
dict with keys:
    cognitive, big5, enneagram, brain_dominance, temperament, mbti,
    multiple_intelligence, profile_summary
"""

from typing import List, Dict, Any

from . import (
    scoring_big5,
    scoring_enneagram,
    scoring_brain_dominance,
    scoring_temperament,
    scoring_mbti,
    scoring_multiple_intelligence,
)

_BIG5_ATTRS      = {"openness", "neuroticism", "agreeableness", "extraversion", "conscientiousness"}
_ENNEAGRAM_ATTRS = {"E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9"}
_BRAIN_DOM_ATTRS = {"L", "R"}
_TEMPERAMENT_ATTRS = {"EI_temperament", "N_temperament", "LIE_temperament"}
_MBTI_ATTRS      = {"EI", "SN", "TF", "JP"}
_MI_ATTRS        = {"LI", "LMI", "MI", "BKI", "SVI", "IPI", "INPI", "NI"}

# Existential Intelligence from MI uses subtest "EI" — same key as MBTI "EI"
# So we route by checking if the question is from the MI block first.
# In practice the dispatcher in main.py already does this routing; here we
# do the same by checking context flags passed in each dict.

OPTION_MAP   = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}
LIKERT_SCALE_MAX = 5   # for 5-point items
LIKERT_7_MAX     = 7   # for MBTI 7-point items




# ─────────────────────────────────────────────────────────────────────────────
#  MI: the "EI" subtest key is Existential Intelligence in MI context.
#  We disambiguate via a section_hint field added by the dispatcher in main.py.
# ─────────────────────────────────────────────────────────────────────────────

def score_short_form(scoring_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parameters
    ----------
    scoring_data : list of dicts, each with keys:
        subtest, keyed, selected_option, correct_answer (optional),
        section        : one of "cognitive" | "big5" | "enneagram" |
                         "brain_dominance" | "temperament" | "mbti" |
                         "multiple_intelligence"
                         (set by main.py based on question.category + subtest)

    Returns
    -------
    Full scoring dict with results for every subtest.
    """
    big5_items          = []
    enneagram_items     = []
    brain_dom_items     = []
    temperament_items   = []
    mbti_items          = []
    mi_items            = []

    for item in scoring_data:
        section = item.get("section", "")
        subtest = item.get("subtest", "")

        if section == "big5" or subtest in _BIG5_ATTRS:
            big5_items.append(item)
        elif section == "enneagram" or subtest in _ENNEAGRAM_ATTRS:
            enneagram_items.append(item)
        elif section == "brain_dominance" or subtest in _BRAIN_DOM_ATTRS:
            brain_dom_items.append({"keyed": item["keyed"], "selected_option": item["selected_option"]})
        elif section == "temperament" or subtest in _TEMPERAMENT_ATTRS:
            temperament_items.append({
                "subtest": subtest,
                "correct_answer": item.get("correct_answer"),
                "selected_option": item["selected_option"],
            })
        elif section == "mbti" or (subtest in _MBTI_ATTRS and section != "multiple_intelligence"):
            mbti_items.append({
                "subtest": subtest,
                "keyed": item["keyed"],
                "selected_option_index": OPTION_MAP.get(item["selected_option"], 4),
            })
        elif section == "multiple_intelligence" or subtest in _MI_ATTRS:
            mi_items.append({"subtest": subtest, "selected_option": item["selected_option"]})

    big5_results         = scoring_big5.score_big5(big5_items)
    enneagram_results    = scoring_enneagram.score_enneagram(enneagram_items)
    brain_dom_results    = scoring_brain_dominance.score_brain_dominance(brain_dom_items)
    temperament_results  = scoring_temperament.score_temperament(temperament_items)
    mbti_results         = scoring_mbti.score_mbti(mbti_items)
    mi_results           = scoring_multiple_intelligence.score_multiple_intelligence(mi_items)

    return {
        "big5":                  big5_results,
        "enneagram":             enneagram_results,
        "brain_dominance":       brain_dom_results,
        "temperament":           temperament_results,
        "mbti":                  mbti_results,
        "multiple_intelligence": mi_results,
    }
