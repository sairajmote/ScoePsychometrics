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
