"""
scoring_brain_dominance.py
Scores 40 Brain Dominance questionnaire responses.

Tendency Keys
-------------
  "L" → Left-brain tendency   (odd-numbered questions: 1,3,5,…,39)
  "R" → Right-brain tendency  (even-numbered questions: 2,4,6,…,40)

Scoring Logic
-------------
  5-point Likert: A=1, B=2, C=3, D=4, E=5
  Left  score  = sum of raw scores for all "L"-keyed questions
  Right score  = sum of raw scores for all "R"-keyed questions

  Each side has 20 questions × max 5 = 100 pts, min 20 pts.
  Percentage: (sum - 20) / 80 * 100  →  maps [20, 100] to [0%, 100%]

Dominant Side
-------------
  left_pct > right_pct  → Left-Brain Dominant
  right_pct > left_pct  → Right-Brain Dominant
  equal                 → Balanced / Whole-Brain

Descriptors (per side percentage)
----------------------------------
  0–30%  : Very Low
  31–45% : Low
  46–60% : Moderate
  61–75% : High
  76–100%: Very High
"""

from typing import List, Dict, Any

OPTION_MAP = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}

SIDE_LABELS = {
    "left":  "Left Brain",
    "right": "Right Brain",
}

SIDE_DESCRIPTIONS = {
    "left": {
        "very_low":  "Very little preference for logical, sequential thinking; structure and analysis feel unnatural.",
        "low":       "Limited inclination toward analytical or structured approaches; prefers intuitive over methodical.",
        "moderate":  "Some use of logical reasoning; balances analysis with intuition in decision-making.",
        "high":      "Clear preference for analytical thinking, order, and fact-based reasoning.",
        "very_high": "Strongly analytical, methodical, and detail-oriented; excels in logic and sequential problem-solving.",
    },
    "right": {
        "very_low":  "Little inclination toward creativity or imagination; prefers concrete and conventional approaches.",
        "low":       "Somewhat conventional; creativity and spontaneity are not primary drivers.",
        "moderate":  "Comfortable with creative tasks; shows some imaginative and intuitive tendencies.",
        "high":      "Noticeably creative, imaginative, and drawn to expressive or artistic pursuits.",
        "very_high": "Highly creative and intuitive; strongly guided by imagination, emotion, and big-picture thinking.",
    },
}

DOMINANCE_PROFILES = {
    "left_dominant": {
        "label":       "Left-Brain Dominant",
        "description": (
            "You exhibit a strong preference for logical, analytical, and structured thinking. "
            "You are likely systematic in your approach to problems, comfortable with numbers and data, "
            "and tend to plan carefully before acting."
        ),
    },
    "right_dominant": {
        "label":       "Right-Brain Dominant",
        "description": (
            "You exhibit a strong preference for creative, intuitive, and holistic thinking. "
            "You are likely imaginative and spontaneous, drawn to art and expression, "
            "and tend to trust your instincts over strict plans."
        ),
    },
    "balanced": {
        "label":       "Balanced / Whole-Brain",
        "description": (
            "You show a relatively equal balance between left-brain analytical reasoning and "
            "right-brain creative intuition. You can adapt your thinking style to suit different "
            "situations, making you a versatile and flexible thinker."
        ),
    },
}


def _descriptor(pct: float) -> str:
    if pct < 30:
        return "very_low"
    elif pct < 45:
        return "low"
    elif pct < 60:
        return "moderate"
    elif pct < 76:
        return "high"
    else:
        return "very_high"


def _descriptor_label(key: str) -> str:
    return {
        "very_low": "Very Low",
        "low":       "Low",
        "moderate":  "Moderate",
        "high":      "High",
        "very_high": "Very High",
    }.get(key, "Moderate")


def score_brain_dominance(scoring_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parameters
    ----------
    scoring_data : list of dicts, each with keys:
        keyed          : "L" (left) or "R" (right)
        selected_option: "A" | "B" | "C" | "D" | "E"

    Returns
    -------
    dict with left/right scores, dominant side, and descriptive profile.
    """
    left_sum  = 0
    right_sum = 0
    left_count  = 0
    right_count = 0

    for item in scoring_data:
        keyed  = item.get("keyed", "").upper()
        option = item.get("selected_option", "C")
        raw    = OPTION_MAP.get(option, 3)  # default neutral

        if keyed == "L":
            left_sum   += raw
            left_count += 1
        elif keyed == "R":
            right_sum   += raw
            right_count += 1

    # Calculate percentages (handle edge case of missing responses)
    if left_count > 0:
        left_pct = round((left_sum  - left_count)  / (left_count  * 4) * 100, 1)
    else:
        left_pct = 50.0

    if right_count > 0:
        right_pct = round((right_sum - right_count) / (right_count * 4) * 100, 1)
    else:
        right_pct = 50.0

    # Determine dominant side (5-point margin to avoid declaring a split on tiny differences)
    margin = left_pct - right_pct
    if margin > 5:
        dominance_key = "left_dominant"
    elif margin < -5:
        dominance_key = "right_dominant"
    else:
        dominance_key = "balanced"

    left_desc_key  = _descriptor(left_pct)
    right_desc_key = _descriptor(right_pct)

    return {
        "left": {
            "label":       SIDE_LABELS["left"],
            "score_pct":   left_pct,
            "descriptor":  _descriptor_label(left_desc_key),
            "description": SIDE_DESCRIPTIONS["left"][left_desc_key],
        },
        "right": {
            "label":       SIDE_LABELS["right"],
            "score_pct":   right_pct,
            "descriptor":  _descriptor_label(right_desc_key),
            "description": SIDE_DESCRIPTIONS["right"][right_desc_key],
        },
        "dominance": {
            "key":         dominance_key,
            "label":       DOMINANCE_PROFILES[dominance_key]["label"],
            "description": DOMINANCE_PROFILES[dominance_key]["description"],
            "left_pct":    left_pct,
            "right_pct":   right_pct,
        },
    }
