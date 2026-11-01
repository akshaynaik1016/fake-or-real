from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

SEEDED_DEMO_CASES: List[Dict[str, Any]] = [
    {
        "id": "demo-fake-msft-internship",
        "title": "Fake Microsoft AI Internship Scam",
        "category": "fake_internship",
        "input_type": "text",
        "claimed_organization": "Microsoft",
        "target_identifier": "Microsoft Corporation",
        "content": (
            "From: Microsoft Careers <recruiter@microsoft-careers-india.xyz>\n\n"
            "Congratulations! You have been officially selected for the Microsoft AI Summer Internship 2026.\n"
            "Role: Junior AI & ML Research Intern\n"
            "Stipend: ₹45,000 / month\n"
            "Requirements: No prior experience needed, 2 hours/day remote work.\n"
            "Registration Fee: Pay ₹999 mandatory refundable laptop security deposit.\n"
            "Official Portal: https://microsoft-careers-india.xyz/apply/onboarding\n"
            "Payment UPI: microsoft.careers@okhdfcbank\n"
            "Required Documents: Submit Aadhaar Card, PAN Card, and Bank Account IFSC.\n"
            "Contact: Recruiter Priya Sharma (HR Talent Lead)\n"
            "Urgency: Only 2 slots remaining. Pay within 24 hours or selection is canceled."
        ),
        "expected_risk": "CRITICAL RISK",
        "description": "Seeded hackathon benchmark test: Impersonates Microsoft, newly registered .xyz domain, ₹999 deposit, Aadhaar/PAN collection."
    },
    {
        "id": "demo-genuine-tcs-opportunity",
        "title": "Synthetic TCS domain-reference comparison",
        "category": "legitimate_opportunity",
        "input_type": "text",
        "claimed_organization": "TCS",
        "target_identifier": "Tata Consultancy Services Limited",
        "content": (
            "Tata Consultancy Services (TCS) invites applications for the National Qualifier Test (NQT) 2026.\n"
            "Eligibility: Pre-final and final year engineering and science students.\n"
            "Official Application URL: https://nextstep.tcs.com/campus/#/register\n"
            "Official Domain: tcs.com\n"
            "Application Fee: There is NO registration fee or security deposit of any kind.\n"
            "Corporate Identifier: CIN L22210MH1995PLC084781 (MCA / ROC Mumbai)\n"
            "Selection is strictly merit-based following the nationwide assessment."
        ),
        "expected_risk": "UNDETERMINED",
        "description": "Synthetic reference comparison only; no live registry, recruiter or specific offer authentication. A no-fee claim does not verify the offer."
    },
    {
        "id": "demo-fake-google-scholarship",
        "title": "Fake Google Generation Scholarship Scheme",
        "category": "fake_scholarship",
        "input_type": "text",
        "claimed_organization": "Google",
        "target_identifier": "Google LLC",
        "content": (
            "Congratulations! Your application has been approved for the Google Tech Future Scholarship Award of $5,000.\n"
            "Portal: https://scholarship-portal-gov.online/verify\n"
            "Processing Charge: Pay $250 international dispatch fee via Western Union or Crypto.\n"
            "Send OTP and account verification code to receive instant bank wire.\n"
            "Act immediately! Claim expires in 4 hours."
        ),
        "expected_risk": "CRITICAL RISK",
        "description": "Scholarship advance-fee fraud: asks for OTP, crypto wire, and charges an upfront processing fee."
    },
    {
        "id": "demo-phishing-upi-portal",
        "title": "Banking / UPI KYC Suspension Phishing Alert",
        "category": "phishing_website",
        "input_type": "url",
        "claimed_organization": "State Bank of India",
        "target_identifier": "State Bank of India",
        "content": "https://sbi-kyc-update-alert.quick-internships-direct.top/login.php?user=verify",
        "expected_risk": "CRITICAL RISK",
        "description": "Phishing portal hosted on disposable .top domain using fake bank branding to harvest NetBanking credentials."
    },
    {
        "id": "demo-freelance-deposit-scam",
        "title": "Freelance Daily Typing / SMS Task Scam",
        "category": "freelance_scam",
        "input_type": "text",
        "claimed_organization": "Direct Work Solutions",
        "target_identifier": "Direct Work Solutions",
        "content": (
            "Work from home daily! Earn ₹3,000 to ₹5,000 per day with simple SMS sending & capcha entry.\n"
            "No skills or degree required. Work on mobile phone anytime.\n"
            "Deposit ₹1,499 refundable software activation fee to recruiter WhatsApp (+91 98765 43210).\n"
            "Immediate daily payouts guaranteed."
        ),
        "expected_risk": "HIGH RISK",
        "description": "Task/freelance deposit scam: Unrealistic payout promises paired with upfront software fee."
    }
]

def get_demo_cases() -> List[Dict[str, Any]]:
    return [{**case,"synthetic":True,"description":"Synthetic scenario, not a real offer. "+case["description"]} for case in SEEDED_DEMO_CASES]

def get_demo_case_by_id(case_id: str) -> Dict[str, Any]:
    for case in SEEDED_DEMO_CASES:
        if case["id"] == case_id:
            return case
    return None
