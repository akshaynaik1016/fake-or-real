import re
from typing import Dict, Any, List

def analyze_salary_anomaly(text: str) -> Dict[str, Any]:
    """
    Analyzes compensation claims vs required hours and experience level.
    Identifies unrealistic 'get rich quick' or inflated salary promises without
    unilaterally declaring fraud based on compensation alone.
    """
    if not text:
        return {"anomaly_detected": False, "flags": []}
        
    flags = []
    text_lower = text.lower()
    
    # Check for "No experience" / "Fresher" / "Students only"
    has_low_barrier = bool(re.search(r"(?i)\b(no\s+experience(\s+needed|\s+required)?|any\s+student|freshers?\s+welcome|no\s+skills?\s+required|anyone\s+can\s+apply)\b", text_lower))
    
    # Check for low hours: "1-2 hours daily", "part time 2 hours"
    has_minimal_hours = bool(re.search(r"(?i)\b([1-3]\s*(hours?|hrs?)\s*(per\s*day|daily|a\s*day)|part\s*time\s*[\d-]+\s*mins?)\b", text_lower))
    
    # Check for compensation claims:
    # Daily: ₹2000-5000/day
    match_daily = re.search(r"(?i)(?:rs\.?|inr|₹|\$)\s*([1-9][0-9]{3,4})\s*(?:per\s*day|\/day|daily)", text_lower)
    # Monthly: ₹50,000 - ₹1,50,000/month
    match_monthly = re.search(r"(?i)(?:rs\.?|inr|₹|\$)\s*([4-9][0-9],[0-9]{3}|[1-9][0-9]{5,})\s*(?:per\s*month|\/month|monthly)", text_lower)
    
    claimed_amount = None
    if match_daily:
        claimed_amount = f"₹{match_daily.group(1)}/day"
    elif match_monthly:
        claimed_amount = f"₹{match_monthly.group(1)}/month"
        
    anomaly_detected = False
    
    # High compensation + (low barrier or minimal hours)
    if claimed_amount and (has_low_barrier or has_minimal_hours):
        anomaly_detected = True
        detail_msg = f"Claimed compensation of {claimed_amount} paired with minimal stated commitment"
        if has_minimal_hours:
            detail_msg += " (1-2 hours/day)"
        if has_low_barrier:
            detail_msg += " and no prior experience requirements"
        detail_msg += ". Compensation appears unusually high compared with the stated entry-level role requirements."
        
        flags.append({
            "code": "COMPENSATION_ANOMALY",
            "severity": "high",
            "message": f"Compensation anomaly: {claimed_amount} for entry-level / minimal hours.",
            "detail": f"{detail_msg} Note: High compensation alone does not prove fraud, but is a prominent hook used by employment and task scams to attract applicants."
        })

    return {
        "anomaly_detected": anomaly_detected,
        "claimed_amount": claimed_amount,
        "has_low_barrier": has_low_barrier,
        "has_minimal_hours": has_minimal_hours,
        "flags": flags
    }
