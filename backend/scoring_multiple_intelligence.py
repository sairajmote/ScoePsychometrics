"""
scoring_multiple_intelligence.py
Scores 90 Multiple Intelligence questionnaire responses.

Intelligence Tags
-----------------
  LI   → Linguistic Intelligence           (10 questions: 22, 30, 38, 41, 45, 46, 47, 48, 49, 50)
  LMI  → Logical-Mathematical Intelligence (10 questions: 3, 8, 10, 13, 20, 21, 40, 51, 52, 53)
  MI   → Musical Intelligence              (10 questions: 2, 17, 18, 34, 42, 54, 55, 56, 57, 58)
  BKI  → Bodily-Kinesthetic Intelligence   (10 questions: 6, 16, 26, 31, 44, 59, 60, 61, 62, 63)
  SVI  → Spatial-Visual Intelligence       (10 questions: 12, 19, 33, 64, 65, 66, 67, 68, 69, 70)
  IPI  → Interpersonal Intelligence        (10 questions: 4, 7, 23, 24, 32, 71, 72, 73, 74, 75)
  INPI → Intrapersonal Intelligence        (10 questions: 1, 11, 14, 25, 37, 76, 77, 78, 79, 80)
  NI   → Naturalistic Intelligence         (10 questions: 9, 28, 29, 35, 43, 81, 82, 83, 84, 85)
  EI   → Existential Intelligence          (10 questions: 5, 15, 27, 36, 39, 86, 87, 88, 89, 90)

Scoring Logic
-------------
  5-point Likert:  A=1  B=2  C=3  D=4  E=5  (all positively keyed)
  Per-intelligence: sum of raw scores for all questions in that group.
  Percentage: (sum - n) / (n * 4) * 100  → maps [n, 5n] to [0%, 100%]
  where n = number of questions in that intelligence group.

Descriptors (per intelligence percentage)
------------------------------------------
  0–30%  : Very Low
  31–45% : Low
  46–60% : Moderate
  61–75% : High
  76–100%: Very High
"""

from typing import List, Dict, Any

INTELLIGENCES = ["LI", "LMI", "MI", "BKI", "SVI", "IPI", "INPI", "NI", "EI"]

INTELLIGENCE_LABELS = {
    "LI":   "Linguistic Intelligence",
    "LMI":  "Logical-Mathematical Intelligence",
    "MI":   "Musical Intelligence",
    "BKI":  "Bodily-Kinesthetic Intelligence",
    "SVI":  "Spatial-Visual Intelligence",
    "IPI":  "Interpersonal Intelligence",
    "INPI": "Intrapersonal Intelligence",
    "NI":   "Naturalistic Intelligence",
    "EI":   "Existential Intelligence",
}

INTELLIGENCE_DESCRIPTIONS = {
    "LI": {
        "very_low":  "Limited interest in language; reading, writing, and word-play feel uninspiring.",
        "low":       "Somewhat disinclined toward linguistic activities; prefers non-verbal forms of expression.",
        "moderate":  "Adequate verbal ability; comfortable with everyday reading and writing tasks.",
        "high":      "Strong verbal aptitude; enjoys writing, reading, and working with language.",
        "very_high": "Exceptional command of language; naturally drawn to storytelling, poetry, and communication.",
    },
    "LMI": {
        "very_low":  "Little affinity for numbers or logical analysis; abstract reasoning feels challenging.",
        "low":       "Somewhat uncomfortable with mathematics or systematic thinking.",
        "moderate":  "Reasonably comfortable with logical tasks; handles everyday numbers and patterns.",
        "high":      "Strong logical-mathematical ability; thrives with data, patterns, and structured reasoning.",
        "very_high": "Highly analytical and mathematically inclined; naturally gravitates toward puzzles, data, and science.",
    },
    "MI": {
        "very_low":  "Little awareness of or interest in music; rhythm and melody have minimal appeal.",
        "low":       "Limited musical sensitivity; music plays a minor role in daily life.",
        "moderate":  "Some appreciation for music; can recognize rhythms and enjoy listening.",
        "high":      "Strong musical awareness; may play an instrument, sing, or deeply engage with music.",
        "very_high": "Exceptional musical intelligence; highly attuned to pitch, rhythm, and musical patterns.",
    },
    "BKI": {
        "very_low":  "Little inclination toward physical activity; fine and gross motor tasks feel unengaging.",
        "low":       "Limited bodily awareness; prefers sedentary or non-physical pursuits.",
        "moderate":  "Comfortable with moderate physical activity; enjoys movement when it serves a purpose.",
        "high":      "Strong bodily-kinesthetic ability; enjoys sports, crafts, dance, or hands-on work.",
        "very_high": "Exceptional physical intelligence; naturally skilled in athletics, craftsmanship, or performance.",
    },
    "SVI": {
        "very_low":  "Limited spatial awareness; navigation and mental visualization feel difficult.",
        "low":       "Somewhat weak spatial sense; prefers verbal or sequential tasks over visual ones.",
        "moderate":  "Adequate visual-spatial ability; can interpret charts and navigate familiar environments.",
        "high":      "Strong spatial intelligence; excellent at visualizing, drawing, and navigating.",
        "very_high": "Exceptional visual-spatial aptitude; naturally gifted at design, architecture, or imagery.",
    },
    "IPI": {
        "very_low":  "Limited interpersonal awareness; social situations may feel awkward or unimportant.",
        "low":       "Somewhat reserved in social contexts; prefers independent work over collaboration.",
        "moderate":  "Reasonably sociable; can cooperate with others and read basic social cues.",
        "high":      "Strong interpersonal skills; empathetic, persuasive, and naturally supportive of others.",
        "very_high": "Exceptional people skills; deeply attuned to others' emotions, motivations, and needs.",
    },
    "INPI": {
        "very_low":  "Limited self-reflection; tends to avoid exploring inner thoughts and emotions.",
        "low":       "Somewhat disconnected from inner life; self-awareness is not a primary focus.",
        "moderate":  "Adequate self-awareness; reflects on personal emotions and reactions when prompted.",
        "high":      "Strong intrapersonal intelligence; regularly reflects on feelings, values, and motivations.",
        "very_high": "Exceptional self-knowledge; deeply introspective and highly attuned to inner emotional states.",
    },
    "NI": {
        "very_low":  "Little connection to the natural world; flora, fauna, and ecosystems hold minimal appeal.",
        "low":       "Limited naturalistic interest; nature is enjoyed occasionally but not deeply explored.",
        "moderate":  "Some appreciation for nature; comfortable outdoors and interested in living things.",
        "high":      "Strong naturalistic intelligence; drawn to the environment, animals, and natural patterns.",
        "very_high": "Exceptional naturalistic awareness; deeply connected to the living world and its systems.",
    },
    "EI": {
        "very_low":  "Little concern with existential or philosophical questions; prefers concrete, practical matters.",
        "low":       "Somewhat disinterested in deep philosophical inquiry; pragmatic over contemplative.",
        "moderate":  "Occasional reflection on life's big questions; open to philosophical discussion.",
        "high":      "Strong existential orientation; regularly contemplates meaning, purpose, and human existence.",
        "very_high": "Profound existential intelligence; deeply engaged with questions of life, death, and ultimate meaning.",
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
        "low":      "Low",
        "moderate": "Moderate",
        "high":     "High",
        "very_high": "Very High",
    }.get(key, "Moderate")


def score_multiple_intelligence(scoring_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parameters
    ----------
    scoring_data : list of dicts, each with keys:
        subtest        : one of INTELLIGENCES (e.g. "LI", "LMI", …)
        selected_option: "A" | "B" | "C" | "D" | "E"

    Returns
    -------
    dict with per-intelligence scores and a dominant-intelligence profile.
    """
    raw_sums = {intel: 0 for intel in INTELLIGENCES}
    counts   = {intel: 0 for intel in INTELLIGENCES}

    for item in scoring_data:
        intel  = (item.get("subtest") or "").upper()
        option = item.get("selected_option", "C")

        if intel not in INTELLIGENCES:
            continue

        raw = OPTION_MAP.get(option, 3)  # default neutral
        raw_sums[intel] += raw
        counts[intel]   += 1

    intelligences_result = {}
    for intel in INTELLIGENCES:
        n = counts[intel]
        if n == 0:
            pct = 50.0
        else:
            total = raw_sums[intel]
            pct = round((total - n) / (n * 4) * 100, 1)

        desc_key = _descriptor(pct)
        intelligences_result[intel] = {
            "label":       INTELLIGENCE_LABELS[intel],
            "score_pct":   pct,
            "descriptor":  _descriptor_label(desc_key),
            "description": INTELLIGENCE_DESCRIPTIONS[intel][desc_key],
        }

    # Find dominant intelligence(s) — those with the highest score
    top_pct = max(v["score_pct"] for v in intelligences_result.values())
    dominant = [
        intel for intel, v in intelligences_result.items()
        if v["score_pct"] >= top_pct - 2  # within 2% of the top score
    ]

    dominant_labels = [INTELLIGENCE_LABELS[d] for d in dominant]
    profile_summary = _build_profile_summary(intelligences_result, dominant_labels)

    return {
        "intelligences": intelligences_result,
        "dominant_intelligences": dominant,
        "dominant_labels": dominant_labels,
        "profile_summary": profile_summary,
    }


def _build_profile_summary(intelligences: Dict[str, Any], dominant_labels: List[str]) -> str:
    if not dominant_labels:
        return "Your Multiple Intelligence profile has been calculated."
    if len(dominant_labels) == 1:
        top = dominant_labels[0]
        return (
            f"Your strongest intelligence is {top}. "
            "This reflects where your natural aptitudes and deepest interests lie. "
            "Review each intelligence area below for a full picture of your unique cognitive profile."
        )
    tops = " and ".join(dominant_labels)
    return (
        f"Your leading intelligences are {tops}. "
        "These reflect where your natural aptitudes and deepest interests are concentrated. "
        "Review each intelligence area below for a full picture of your unique cognitive profile."
    )
