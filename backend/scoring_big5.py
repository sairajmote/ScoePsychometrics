"""
scoring_big5.py
Scores 50 Big 5 Personality questionnaire responses.

Traits
------
  openness          → Openness to Experience (O)
  neuroticism       → Neuroticism            (N)
  agreeableness     → Agreeableness          (A)
  extraversion      → Extraversion           (E)
  conscientiousness → Conscientiousness      (C)

Scoring Logic
-------------
  5-point Likert: A=1, B=2, C=3, D=4, E=5
  Positively keyed (+): score = raw (1–5)
  Negatively keyed (-): score = (6 - raw)   → reverse scored

Per-trait: 10 questions × max 5 points = 50 points max, 10 points min.
Percentage: (sum - 10) / 40 * 100  →  maps [10, 50] to [0%, 100%]

Descriptors (per trait score percentage)
-----------------------------------------
  0–30%  : Very Low
  31–45% : Low
  46–60% : Moderate
  61–75% : High
  76–100%: Very High
"""

from typing import List, Dict, Any

TRAITS = ["openness", "neuroticism", "agreeableness", "extraversion", "conscientiousness"]

TRAIT_LABELS = {
    "openness": "Openness to Experience",
    "neuroticism": "Neuroticism",
    "agreeableness": "Agreeableness",
    "extraversion": "Extraversion",
    "conscientiousness": "Conscientiousness",
}

TRAIT_DESCRIPTIONS = {
    "openness": {
        "very_low":  "Strongly prefers familiar routines and conventional ideas; tends to be practical and traditional.",
        "low":       "Prefers established ways over experimentation; cautious about new or abstract concepts.",
        "moderate":  "Balances curiosity with practicality; open to new ideas when they seem relevant.",
        "high":      "Intellectually curious, creative, and drawn to novel ideas and diverse experiences.",
        "very_high": "Highly imaginative and constantly seeking new knowledge; deeply stimulated by abstract thought and creativity.",
    },
    "neuroticism": {
        "very_low":  "Exceptionally emotionally stable and resilient; rarely experiences stress or negative emotions.",
        "low":       "Generally calm and composed; handles stress well and recovers quickly from setbacks.",
        "moderate":  "Occasional emotional fluctuations; can be sensitive to stress but generally manages well.",
        "high":      "Frequently experiences emotional reactivity; tends to worry and may find stress harder to manage.",
        "very_high": "High levels of emotional sensitivity; prone to anxiety, mood swings, and persistent worry.",
    },
    "agreeableness": {
        "very_low":  "Highly competitive and skeptical; prioritizes personal goals over social harmony.",
        "low":       "Somewhat competitive and direct; candid in communication but not always considerate of others' feelings.",
        "moderate":  "Balances self-interest with cooperation; gets along reasonably well with others.",
        "high":      "Cooperative, empathetic, and genuinely concerned with others' wellbeing.",
        "very_high": "Extremely considerate, trusting, and harmonious; naturally inclined toward helping and accommodating others.",
    },
    "extraversion": {
        "very_low":  "Strongly introverted; energized by solitude and prefers minimal social interaction.",
        "low":       "Prefers quiet, small-group settings; not energized by large social environments.",
        "moderate":  "Comfortable in both social and solitary settings; flexible in social engagement.",
        "high":      "Enjoys social interaction and is energized by group settings; tends to be talkative and assertive.",
        "very_high": "Thrives in highly social, dynamic environments; strongly outgoing, enthusiastic, and sociable.",
    },
    "conscientiousness": {
        "very_low":  "Tends to be spontaneous and flexible; may struggle with organization and follow-through.",
        "low":       "Somewhat disorganized; can be flexible but may lack consistent structure or planning.",
        "moderate":  "Reasonably organized and dependable; balances structure with adaptability.",
        "high":      "Disciplined, goal-oriented, and organized; reliably follows through on commitments.",
        "very_high": "Highly methodical and self-disciplined; consistently plans ahead and maintains strong organizational habits.",
    },
}

OPTION_MAP = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}


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
        "low": "Low",
        "moderate": "Moderate",
        "high": "High",
        "very_high": "Very High",
    }.get(key, "Moderate")


def score_big5(scoring_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parameters
    ----------
    scoring_data : list of dicts, each with keys:
        subtest        : one of TRAITS
        keyed          : "+" or "-"
        selected_option: "A" | "B" | "C" | "D" | "E"

    Returns
    -------
    dict with per-trait scores and overall profile.
    """
    raw_sums = {t: 0 for t in TRAITS}
    counts   = {t: 0 for t in TRAITS}

    for item in scoring_data:
        trait  = (item.get("subtest") or "").lower()
        keyed  = item.get("keyed", "+")
        option = item.get("selected_option", "C")

        if trait not in TRAITS:
            continue

        raw = OPTION_MAP.get(option, 3)  # default neutral
        scored = raw if keyed == "+" else (6 - raw)

        raw_sums[trait] += scored
        counts[trait]   += 1

    traits_result = {}
    for trait in TRAITS:
        n = counts[trait]
        if n == 0:
            pct = 50.0
        else:
            total = raw_sums[trait]
            # Scale: min = n*1, max = n*5  → pct = (total - n) / (n*4) * 100
            pct = round((total - n) / (n * 4) * 100, 1)

        desc_key = _descriptor(pct)
        traits_result[trait] = {
            "label":       TRAIT_LABELS[trait],
            "score_pct":   pct,
            "descriptor":  _descriptor_label(desc_key),
            "description": TRAIT_DESCRIPTIONS[trait][desc_key],
        }

    return {
        "traits": traits_result,
        "profile_summary": _build_profile_summary(traits_result),
    }


def _build_profile_summary(traits: Dict[str, Any]) -> str:
    o  = traits["openness"]["descriptor"]
    n  = traits["neuroticism"]["descriptor"]
    a  = traits["agreeableness"]["descriptor"]
    e  = traits["extraversion"]["descriptor"]
    c  = traits["conscientiousness"]["descriptor"]
    return (
        f"This Big Five profile shows {o} Openness, {n} Neuroticism, "
        f"{a} Agreeableness, {e} Extraversion, and {c} Conscientiousness. "
        "Together these traits describe your characteristic way of thinking, feeling, and interacting with the world."
    )
