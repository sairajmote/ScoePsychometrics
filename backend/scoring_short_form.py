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

_COGNITIVE_ATTRS = {"forgetfulness", "false_triggering", "distractibility", "cognitive"}
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
#  Cognitive scoring (self-report Likert, same +/- logic as Big Five)
# ─────────────────────────────────────────────────────────────────────────────
_COG_LABELS = {
    "forgetfulness":   "Forgetfulness",
    "false_triggering": "False Triggering",
    "distractibility": "Distractibility",
    "cognitive":       "Cognitive (Logic & Sequence)",
}

_COG_DESCRIPTIONS = {
    "forgetfulness": {
        "very_low":  "Excellent working memory; rarely forgets day-to-day details.",
        "low":       "Generally reliable memory with occasional lapses.",
        "moderate":  "Moderate forgetfulness; everyday reminders are occasionally helpful.",
        "high":      "Frequent memory lapses that may affect daily functioning.",
        "very_high": "Persistent and significant difficulty retaining recent information.",
    },
    "false_triggering": {
        "very_low":  "Rarely misreads situations; calm and accurate threat-assessment.",
        "low":       "Occasionally jumps to conclusions but self-corrects quickly.",
        "moderate":  "Sometimes reacts before fully assessing a situation.",
        "high":      "Frequently misinterprets neutral cues as threatening or alarming.",
        "very_high": "Highly reactive; often triggered by false alarms.",
    },
    "distractibility": {
        "very_low":  "Exceptional focus; maintains concentration under most conditions.",
        "low":       "Generally focused with minor susceptibility to distraction.",
        "moderate":  "Moderate distractibility; benefits from structured environments.",
        "high":      "Frequently distracted; sustained attention requires significant effort.",
        "very_high": "Severe difficulty maintaining focus; attention shifts very easily.",
    },
    "cognitive": {
        "very_low":  "Finds sequential and logical reasoning quite challenging.",
        "low":       "Below-average comfort with multi-step logic or sequence tasks.",
        "moderate":  "Adequate logical reasoning; handles most everyday problems competently.",
        "high":      "Strong logical and sequential thinking; spots patterns readily.",
        "very_high": "Exceptional analytical ability; thrives with complex reasoning chains.",
    },
}


def _cog_descriptor(pct: float) -> str:
    if pct < 30: return "very_low"
    if pct < 45: return "low"
    if pct < 60: return "moderate"
    if pct < 76: return "high"
    return "very_high"


def _score_cognitive(items: List[Dict]) -> Dict[str, Any]:
    raw_sums = {a: 0 for a in _COG_ATTRS}
    counts   = {a: 0 for a in _COG_ATTRS}

    for item in items:
        attr   = item["subtest"]
        keyed  = item.get("keyed", "+")
        option = item.get("selected_option", "C")
        if attr not in _COG_ATTRS:
            continue
        raw    = OPTION_MAP.get(option, 3)
        scored = raw if keyed == "+" else (6 - raw)
        raw_sums[attr] += scored
        counts[attr]   += 1

    result = {}
    for attr in _COG_ATTRS:
        n = counts[attr]
        pct = round((raw_sums[attr] - n) / (n * 4) * 100, 1) if n else 50.0
        dk  = _cog_descriptor(pct)
        result[attr] = {
            "label":       _COG_LABELS[attr],
            "score_pct":   pct,
            "descriptor":  dk.replace("_", " ").title(),
            "description": _COG_DESCRIPTIONS[attr][dk],
        }

    top = max(result, key=lambda a: result[a]["score_pct"])
    return {
        "attributes": result,
        "profile_summary": (
            f"Cognitive profile: Forgetfulness {result['forgetfulness']['descriptor']}, "
            f"Distractibility {result['distractibility']['descriptor']}, "
            f"False Triggering {result['false_triggering']['descriptor']}, "
            f"Logical Reasoning {result['cognitive']['descriptor']}. "
            f"Most prominent attribute: {_COG_LABELS[top]}."
        )
    }

_COG_ATTRS = _COGNITIVE_ATTRS   # alias for closure


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
    cognitive_items     = []
    big5_items          = []
    enneagram_items     = []
    brain_dom_items     = []
    temperament_items   = []
    mbti_items          = []
    mi_items            = []

    for item in scoring_data:
        section = item.get("section", "")
        subtest = item.get("subtest", "")

        if section == "cognitive" or subtest in _COGNITIVE_ATTRS:
            cognitive_items.append(item)
        elif section == "big5" or subtest in _BIG5_ATTRS:
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

    cognitive_results    = _score_cognitive(cognitive_items)
    big5_results         = scoring_big5.score_big5(big5_items)
    enneagram_results    = scoring_enneagram.score_enneagram(enneagram_items)
    brain_dom_results    = scoring_brain_dominance.score_brain_dominance(brain_dom_items)
    temperament_results  = scoring_temperament.score_temperament(temperament_items)
    mbti_results         = scoring_mbti.score_mbti(mbti_items)
    mi_results           = scoring_multiple_intelligence.score_multiple_intelligence(mi_items)

    return {
        "cognitive":             cognitive_results,
        "big5":                  big5_results,
        "enneagram":             enneagram_results,
        "brain_dominance":       brain_dom_results,
        "temperament":           temperament_results,
        "mbti":                  mbti_results,
        "multiple_intelligence": mi_results,
    }
