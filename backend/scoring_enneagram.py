"""
scoring_enneagram.py
Scores the 125-item Enneagram questionnaire and identifies the primary type, wing, and dominant center.

Scoring Logic
-------------
  5-point Likert: A=1, B=2, C=3, D=4, E=5
  Each Enneagram type is scored by summing the raw values for all questions
  belonging to that type and normalizing by the number of questions.

Returns
-------
  type_scores : per-type percentage scores
  primary_type: strongest Enneagram type and wing
  center      : head/heart/gut classification
  interpretation: concise summary of the candidate's dominant Enneagram pattern
"""

from typing import List, Dict, Any

OPTION_MAP = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}

TYPE_KEYS = [f"E{i}" for i in range(1, 10)]
TYPE_LABELS = {
    "E1": "The Reformer",
    "E2": "The Helper",
    "E3": "The Achiever",
    "E4": "The Individualist",
    "E5": "The Investigator",
    "E6": "The Loyalist",
    "E7": "The Enthusiast",
    "E8": "The Challenger",
    "E9": "The Peacemaker",
}

TYPE_CENTERS = {
    "E1": "gut",
    "E2": "heart",
    "E3": "heart",
    "E4": "heart",
    "E5": "head",
    "E6": "head",
    "E7": "head",
    "E8": "gut",
    "E9": "gut",
}

CENTER_LABELS = {
    "head": "Head Center (Thinking)",
    "heart": "Heart Center (Feeling)",
    "gut": "Gut Center (Instinctive)",
}

CENTER_MOTIVATIONS = {
    "head": "seeking clarity, certainty, and mental mastery",
    "heart": "seeking connection, identity, and emotional authenticity",
    "gut": "seeking control, autonomy, and ethical integrity",
}

TYPE_INTERPRETATIONS = {
    "E1": "You are principled, responsible, and driven by a desire for improvement and integrity.",
    "E2": "You are warm, generous, and motivated by a deep need to feel loved and needed.",
    "E3": "You are ambitious, adaptable, and focused on achievement, success, and recognition.",
    "E4": "You are introspective, creative, and attuned to your emotional depth and individuality.",
    "E5": "You are perceptive, curious, and value knowledge, privacy, and mental independence.",
    "E6": "You are loyal, cautious, and driven by a need for security, support, and trust.",
    "E7": "You are enthusiastic, spontaneous, and motivated by a desire for freedom and positive possibilities.",
    "E8": "You are assertive, decisive, and energized by strength, justice, and direct action.",
    "E9": "You are easygoing, accepting, and oriented toward harmony, peace, and stability.",
}


def _descriptor(pct: float) -> str:
    if pct < 25:
        return "low"
    elif pct < 45:
        return "moderate"
    elif pct < 65:
        return "strong"
    else:
        return "dominant"


def score_enneagram(scoring_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    raw_sums = {key: 0 for key in TYPE_KEYS}
    counts = {key: 0 for key in TYPE_KEYS}

    for item in scoring_data:
        subtest = (item.get("subtest") or "").upper()
        option = item.get("selected_option", "C").upper()
        if subtest not in TYPE_KEYS:
            continue

        raw = OPTION_MAP.get(option, 3)
        raw_sums[subtest] += raw
        counts[subtest] += 1

    type_scores = {}
    for key in TYPE_KEYS:
        n = counts[key]
        if n > 0:
            pct = round((raw_sums[key] - n) / (n * 4) * 100, 1)
        else:
            pct = 0.0

        type_scores[f"type_{TYPE_KEYS.index(key) + 1}"] = {
            "label": TYPE_LABELS[key],
            "score_pct": pct,
            "descriptor": _descriptor(pct),
        }

    # Determine the strongest type and the wings
    sorted_scores = sorted(type_scores.items(), key=lambda x: x[1]["score_pct"], reverse=True)
    primary_key, primary_data = sorted_scores[0]
    primary_type_number = int(primary_key.split("_")[1])
    primary_type_code = f"E{primary_type_number}"
    primary_label = TYPE_LABELS[primary_type_code]
    primary_center = TYPE_CENTERS[primary_type_code]

    left_wing_type = primary_type_number - 1 if primary_type_number > 1 else 9
    right_wing_type = primary_type_number + 1 if primary_type_number < 9 else 1
    left_key = f"type_{left_wing_type}"
    right_key = f"type_{right_wing_type}"
    left_pct = type_scores[left_key]["score_pct"]
    right_pct = type_scores[right_key]["score_pct"]
    if right_pct > left_pct:
        wing_number = right_wing_type
    else:
        wing_number = left_wing_type

    wing_code = f"{primary_type_number}w{wing_number}"
    wing_label = TYPE_LABELS[f"E{wing_number}"]

    primary_score = primary_data["score_pct"]
    interpretation = (
        f"Your dominant Enneagram type is {primary_type_number} — {primary_label}. "
        f"This profile suggests a core focus on {TYPE_INTERPRETATIONS[primary_type_code][:-1].lower()} and a strong connection to the {CENTER_LABELS[primary_center]}. "
        f"Your stronger wing appears to be {wing_code} ({wing_label})."
    )

    return {
        "type_scores": type_scores,
        "primary_type": {
            "number": primary_type_number,
            "code": primary_type_code,
            "label": primary_label,
            "wing": wing_code,
            "wing_label": wing_label,
            "score_pct": primary_score,
            "descriptor": primary_data["descriptor"],
        },
        "center": {
            "key": primary_center,
            "label": CENTER_LABELS[primary_center],
            "core_motivation": CENTER_MOTIVATIONS[primary_center],
        },
        "type_rankings": [
            {
                "type": int(key.split("_")[1]),
                "label": value["label"],
                "score_pct": value["score_pct"],
                "descriptor": value["descriptor"],
            }
            for key, value in sorted_scores
        ],
        "interpretation": interpretation,
    }
