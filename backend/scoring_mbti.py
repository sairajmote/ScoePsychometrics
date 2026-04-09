import numpy as np
from typing import Dict, List, Any

def score_mbti(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Scores MBTI responses based on the logic from mbit_tester.py.
    
    responses: List of dicts with {'question_id', 'selected_option_index', 'subtest', 'keyed'}
               selected_option_index: 1 for A, 2 for B, ... 7 for G
    """
    dimensions = ["EI", "SN", "TF", "JP"]
    first_letters = {"EI": "E", "SN": "S", "TF": "T", "JP": "J"}
    
    dim_items = {d: [] for d in dimensions}
    
    for resp in responses:
        dim = resp['subtest']
        keyed = resp['keyed']
        raw = resp['selected_option_index'] # 1 to 7
        
        direction = 1 if keyed == "+" else -1
        scored = raw if direction == 1 else (8 - raw)
        
        if dim in dim_items:
            dim_items[dim].append(scored)
            
    mbti_result = ""
    dim_details = {}
    
    midpoint = 4.0
    
    for dim in dimensions:
        items = np.array(dim_items[dim])
        if len(items) == 0:
            dim_details[dim] = {
                "mean": 4.0,
                "letter": first_letters[dim],
                "clarity": 0.0,
                "pct_a": 50.0,
                "pct_b": 50.0
            }
            continue
            
        mean_score = items.mean()
        
        # Letter based on mean >= 4.0
        # In mbit_tester: letter = first_letters[dim] if mean_score >= midpoint else dim[1]
        letter = first_letters[dim] if mean_score >= midpoint else dim[1]
        mbti_result += letter
        
        # Clarity/Clarity Score
        clarity_score = abs(mean_score - midpoint) / 3.0 * 100
        
        # Map mean 1-7 to 0-100 for dichotomy visualization
        # 1 -> 100% Introvert, 7 -> 100% Extrovert? 
        # Actually mbit_tester uses mean_score. 
        # To show percentages for A/B (e.g. E vs I):
        # If mean is 7, it's 100% E. If mean is 1, it's 100% I. 
        # (mean - 1) / 6 * 100 = percentage of first letter
        pct_first = (mean_score - 1) / 6 * 100
        pct_second = 100 - pct_first
        
        dim_details[dim] = {
            "mean": float(mean_score),
            "letter": letter,
            "clarity": float(clarity_score),
            "pct_a": float(pct_first),
            "pct_b": float(pct_second)
        }
        
    return {
        "result_type": mbti_result,
        "dimensions": dim_details
    }

def get_mbti_label(mbti_type: str) -> str:
    labels = {
        "ISTJ": "The Inspector", "ISFJ": "The Protector", "INFJ": "The Advocate", "INTJ": "The Architect",
        "ISTP": "The Crafter", "ISFP": "The Artist", "INFP": "The Mediator", "INTP": "The Thinker",
        "ESTP": "The Persuader", "ESFP": "The Performer", "ENFP": "The Champion", "ENTP": "The Visionary",
        "ESTJ": "The Director", "ESFJ": "The Caregiver", "ENFJ": "The Protagonist", "ENTJ": "The Commander"
    }
    return labels.get(mbti_type, "Unknown Type")

MBTI_FUNCTION_STACKS = {
    "INTJ": {
        "dominant": {"code": "Ni", "label": "Introverted Intuition", "description": "Processing information through internal patterns and future possibilities."},
        "auxiliary": {"code": "Te", "label": "Extraverted Thinking", "description": "Organizing and structuring the external world for efficiency."},
        "tertiary": {"code": "Fi", "label": "Introverted Feeling", "description": "Processing values and internal harmony."},
        "inferior": {"code": "Se", "label": "Extraverted Sensing", "description": "Experiencing the immediate physical world."}
    },
    "INFJ": {
        "dominant": {"code": "Ni", "label": "Introverted Intuition", "description": "Seeking deep meaning and connection in the world of ideas."},
        "auxiliary": {"code": "Fe", "label": "Extraverted Feeling", "description": "Connecting with others through shared values and harmony."},
        "tertiary": {"code": "Ti", "label": "Introverted Thinking", "description": "Analyzing information through internal logic."},
        "inferior": {"code": "Se", "label": "Extraverted Sensing", "description": "Living in the present moment through the senses."}
    },
    "ISTJ": {
        "dominant": {"code": "Si", "label": "Introverted Sensing", "description": "Recalling and relying on past experiences and data."},
        "auxiliary": {"code": "Te", "label": "Extraverted Thinking", "description": "Applying logic and order to reach tangible results."},
        "tertiary": {"code": "Fi", "label": "Introverted Feeling", "description": "Internal values-based decision making."},
        "inferior": {"code": "Ne", "label": "Extraverted Intuition", "description": "Exploring new possibilities and patterns."}
    },
    "ISFJ": {
        "dominant": {"code": "Si", "label": "Introverted Sensing", "description": "Applying past knowledge to care for others and maintain tradition."},
        "auxiliary": {"code": "Fe", "label": "Extraverted Feeling", "description": "Focusing on social harmony and the needs of others."},
        "tertiary": {"code": "Ti", "label": "Introverted Thinking", "description": "Analyzing data through personal logical frameworks."},
        "inferior": {"code": "Ne", "label": "Extraverted Intuition", "description": "Discovering new ideas and future potential."}
    },
    "INTP": {
        "dominant": {"code": "Ti", "label": "Introverted Thinking", "description": "Seeking internal consistency and logical precision."},
        "auxiliary": {"code": "Ne", "label": "Extraverted Intuition", "description": "Exploring a variety of ideas and abstract possibilities."},
        "tertiary": {"code": "Si", "label": "Introverted Sensing", "description": "Connecting new data to known facts and experiences."},
        "inferior": {"code": "Fe", "label": "Extraverted Feeling", "description": "Seeking connection and social harmony."}
    },
    "INFP": {
        "dominant": {"code": "Fi", "label": "Introverted Feeling", "description": "Processing the world through core personal values and authenticity."},
        "auxiliary": {"code": "Ne", "label": "Extraverted Intuition", "description": "Exploring creative possibilities and new perspectives."},
        "tertiary": {"code": "Si", "label": "Introverted Sensing", "description": "Connecting to personal history and sensory details."},
        "inferior": {"code": "Te", "label": "Extraverted Thinking", "description": "Organizing tasks and systems for practical results."}
    },
    "ISTP": {
        "dominant": {"code": "Ti", "label": "Introverted Thinking", "description": "Analyzing manual or technical systems with logical precision."},
        "auxiliary": {"code": "Se", "label": "Extraverted Sensing", "description": "Interacting directly with the physical environment."},
        "tertiary": {"code": "Ni", "label": "Introverted Intuition", "description": "Developing internal insights and long-term patterns."},
        "inferior": {"code": "Fe", "label": "Extraverted Feeling", "description": "Seeking social connection and group values."}
    },
    "ISFP": {
        "dominant": {"code": "Fi", "label": "Introverted Feeling", "description": "Living authentically through personal values and aesthetics."},
        "auxiliary": {"code": "Se", "label": "Extraverted Sensing", "description": "Sensing and reacting to the immediate physical beauty."},
        "tertiary": {"code": "Ni", "label": "Introverted Intuition", "description": "Perceiving underlying meanings and future trends."},
        "inferior": {"code": "Te", "label": "Extraverted Thinking", "description": "Implementing practical plans and objective logic."}
    },
    "ENTJ": {
        "dominant": {"code": "Te", "label": "Extraverted Thinking", "description": "Leading and organizing systems for maximum achievement."},
        "auxiliary": {"code": "Ni", "label": "Introverted Intuition", "description": "Visioning long-term goals and strategic patterns."},
        "tertiary": {"code": "Se", "label": "Extraverted Sensing", "description": "Exploiting immediate opportunities in the environment."},
        "inferior": {"code": "Fi", "label": "Introverted Feeling", "description": "Connecting with personal ethics and internal values."}
    },
    "ENFJ": {
        "dominant": {"code": "Fe", "label": "Extraverted Feeling", "description": "Leading others through empathy and shared group values."},
        "auxiliary": {"code": "Ni", "label": "Introverted Intuition", "description": "Intuiting the growth potential and needs of others."},
        "tertiary": {"code": "Se", "label": "Extraverted Sensing", "description": "Enjoying the sensory details of the present moment."},
        "inferior": {"code": "Ti", "label": "Introverted Thinking", "description": "Categorizing and analyzing data logically."}
    },
    "ESTJ": {
        "dominant": {"code": "Te", "label": "Extraverted Thinking", "description": "Implementing order and standard operating procedures."},
        "auxiliary": {"code": "Si", "label": "Introverted Sensing", "description": "Using proven methods and reliable data from the past."},
        "tertiary": {"code": "Ne", "label": "Extraverted Intuition", "description": "Finding new ways to solve practical problems."},
        "inferior": {"code": "Fi", "label": "Introverted Feeling", "description": "Understanding personal values and internal harmony."}
    },
    "ESFJ": {
        "dominant": {"code": "Fe", "label": "Extraverted Feeling", "description": "Organizing clear social structures to care for people's needs."},
        "auxiliary": {"code": "Si", "label": "Introverted Sensing", "description": "Relying on tradition and past social norms."},
        "tertiary": {"code": "Ne", "label": "Extraverted Intuition", "description": "Seeking out new social experiences and variety."},
        "inferior": {"code": "Ti", "label": "Introverted Thinking", "description": "Analyzing information through logical frameworks."}
    },
    "ENTP": {
        "dominant": {"code": "Ne", "label": "Extraverted Intuition", "description": "Brainstorming and exploring a wide range of innovative ideas."},
        "auxiliary": {"code": "Ti", "label": "Introverted Thinking", "description": "Testing ideas against a rigorous internal logical system."},
        "tertiary": {"code": "Fe", "label": "Extraverted Feeling", "description": "Engaging others and reading social dynamics."},
        "inferior": {"code": "Si", "label": "Introverted Sensing", "description": "Grounding ideas in facts and previous experiences."}
    },
    "ENFP": {
        "dominant": {"code": "Ne", "label": "Extraverted Intuition", "description": "Seeing endless possibilities and enthusiastic potential in the world."},
        "auxiliary": {"code": "Fi", "label": "Introverted Feeling", "description": "Ensuring actions align with deep personal values."},
        "tertiary": {"code": "Te", "label": "Extraverted Thinking", "description": "Setting plans and logic to achieve visions."},
        "inferior": {"code": "Si", "label": "Introverted Sensing", "description": "Relating new concepts back to known traditions."}
    },
    "ESTP": {
        "dominant": {"code": "Se", "label": "Extraverted Sensing", "description": "Boldly interacting with the immediate physical environment."},
        "auxiliary": {"code": "Ti", "label": "Introverted Thinking", "description": "Quickly analyzing situations through logical frameworks."},
        "tertiary": {"code": "Fe", "label": "Extraverted Feeling", "description": "Navigating social interactions with charm and influence."},
        "inferior": {"code": "Ni", "label": "Introverted Intuition", "description": "Identifying future implications and patterns."}
    },
    "ESFP": {
        "dominant": {"code": "Se", "label": "Extraverted Sensing", "description": "Enthusiastically engaging with and entertaining the world."},
        "auxiliary": {"code": "Fi", "label": "Introverted Feeling", "description": "Responding to personal values and emotional authenticity."},
        "tertiary": {"code": "Te", "label": "Extraverted Thinking", "description": "Implementing and finishing practical tasks."},
        "inferior": {"code": "Ni", "label": "Introverted Intuition", "description": "Sensing hidden meanings and future possibilities."}
    }
}

def get_cognitive_stack(mbti_type: str) -> Dict[str, Dict[str, str]]:
    """Returns the cognitive function stack for a given MBTI type."""
    return MBTI_FUNCTION_STACKS.get(mbti_type, {
        "dominant": {"code": "??", "label": "Unknown", "description": "N/A"},
        "auxiliary": {"code": "??", "label": "Unknown", "description": "N/A"},
        "tertiary": {"code": "??", "label": "Unknown", "description": "N/A"},
        "inferior": {"code": "??", "label": "Unknown", "description": "N/A"}
    })


# Reverse scoring — questions that point toward the second letter of a dimension (e.g. I, N, F, P) are now flipped (8 - raw) before scoring, which is a core CTT requirement
# Mean score per dimension — clean CTT total score, classified against the midpoint (4.0 on a 1–7 scale)
#Preference clarity % — tells the user how strongly they lean in a direction, not just which side they're on
#Cronbach's Alpha — standard CTT reliability estimate per dimension, so you can see how internally consiste