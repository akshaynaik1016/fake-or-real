from app.schemas.investigation import Recommendation


def recommend(entities: list[dict], evidence: list[dict], history: list[dict],
              research_available: bool, remaining_searches: int, reference_available: bool = True) -> list[dict]:
    completed = {h["action_id"] for h in history if h.get("status") == "COMPLETED"}
    types = {e["type"] for e in entities}
    actions = []
    def add(action, title, reason, rank, automated, available, instructions, required, unavailable_reason=None):
        actions.append(Recommendation(action_id=action, title=title, reason=reason,
            priority="HIGH" if rank >= 80 else "MEDIUM" if rank >= 50 else "LOW",
            ranking_score=rank, execution_type="AUTOMATED" if automated else "MANUAL",
            status="COMPLETED" if action in completed else "AVAILABLE" if available else "UNAVAILABLE",
            instructions=instructions, required_information=required,
            unavailable_reason=unavailable_reason if not available else None,
            expected_outcomes=["Recorded match or mismatch" if action == "verify_sender_domain" else
                               "Additional independent context or an explicit unresolved result",
                               "An organization match alone does not authenticate this offer"]).model_dump())
    if "email" in types:
        add("verify_sender_domain", "Compare sender domain with organization reference", 
            "Identity is unresolved; a local reference comparison is fast and requires no external service.",
            100, True, "organization" in types and reference_available,
            "Compare the submitted sender domain with the bundled organization reference. This does not verify email delivery or recruiter authorization.", ["Sender email", "Claimed organization"], "No matching organization reference or sender address is available.")
    if "organization" in types:
        add("research_warnings", "Search independent recruitment and scam context",
            "Independent context may resolve unanswered identity questions. One bounded search; no automatic authenticity verdict.",
            85, True, research_available and remaining_searches > 0,
            "Search Tavily for organization recruitment warnings; inspect dated sources and independently contact the organization.", ["Claimed organization", "Tavily configuration and remaining search budget"],
            "Research search budget exhausted." if remaining_searches <= 0 else "TAVILY_API_KEY is not configured.")
        add("contact_organization", "Verify recruiter through an independently found contact",
            "Only an authorized organization contact can confirm the specific offer and recruiter.",
            90, False, True,
            "Type the organization's known official website yourself. Find recruitment contact details there and ask whether this exact recruiter, role and fee request are authorized. Do not use contact details supplied in the offer.", ["Exact role and recruiter details"])
    if any(e["category"] == "payment_risk" for e in evidence):
        add("verify_payment", "Verify the payment demand before sending money",
            "An unresolved upfront payment request has direct financial consequences.",
            95, False, True,
            "Pause payment. Ask the organization using an independently sourced contact whether any fee is required. Preserve the payment identifier and offer. Do not send a test payment.", ["Payment request"])
    if not actions:
        add("obtain_details", "Obtain an official listing and sender details",
            "Insufficient independent details are available for investigation.",
            80, False, True, "Obtain the original email headers, official role listing and claimed organization name before proceeding.", ["Original offer"])
    return sorted(actions, key=lambda a: (-a["ranking_score"], a["action_id"]))
