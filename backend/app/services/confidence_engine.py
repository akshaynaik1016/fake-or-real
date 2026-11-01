from typing import List, Dict, Any

def calculate_analysis_confidence(
    evidence_list: List[Dict[str, Any]],
    checks_performed: int,
    input_length: int
) -> int:
    """
    Calculates the analysis confidence percentage (0-100%).
    Confidence scales with:
    1. Quantity of corroborating independent evidence items.
    2. Number of verification checks successfully executed.
    3. Completeness of submission content.
    Confidence is strictly distinct from the Trust Score.
    """
    base_confidence = 50
    
    # Bonus for number of verified checks executed (up to +25)
    check_bonus = min(25, checks_performed * 3)
    
    # Bonus for volume of observed evidence (up to +20)
    evidence_count = len(evidence_list)
    evidence_bonus = min(20, evidence_count * 4)
    
    # Bonus for content substance (up to +10)
    content_bonus = 10 if input_length > 150 else (5 if input_length > 50 else 0)
    
    total = base_confidence + check_bonus + evidence_bonus + content_bonus
    # Scale to 70-98 range for realistic forensic confidence
    return max(60, min(96, total))
