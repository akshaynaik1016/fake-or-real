# Judge walkthrough — no model or API key required

1. Start backend/frontend using README.md. Leave AI_PROVIDER=none,
   TAVILY_API_KEY empty and NETWORK_SCANNERS_ENABLED=false.
2. Open `/demo`. Its banner identifies synthetic offers and fixture data.
3. Run the Microsoft internship scenario: ₹45,000/month, ₹999 upfront fee,
   unverified sender/domain and Aadhaar/PAN request. The original scanners run;
   synthetic domain/TLS/threat fixtures are explicitly labelled and excluded from
   the new fusion assessment. Observed submitted language and reference mismatches
   remain rule evidence. Do not claim these fixtures are live external research.
4. Inspect Evidence Fusion: heuristic mode, risk score, evidence confidence and
   partial coverage. Expand calculation/unknowns to see grouped contributions.
   A high risk score can coexist with low coverage; there is no validated probability.
5. The investigation summary says deterministic/FALLBACK. No Gemma response is
   simulated. The AI Investigator button uses the preserved deterministic Q&A.
6. Identity and External Research says SEARCH UNAVAILABLE when no Tavily key exists.
   The recommendation remains unavailable. No fabricated search results are shown.
7. Pan/zoom TrustGraph; select the organization, sender/domain or evidence node.
   Inspect provenance and uncertainty. Use the entity list for keyboard access.
8. In Next Best Investigation, execute the local sender-domain comparison. The
   result stores a new evidence record, adds a graph node, advances the revision,
   updates fusion and records why the score changed or stayed the same. A correlated
   mismatch already represented in the assessment should not be counted again.
9. Reload the page: results, evidence IDs and history persist. Download PDF and
   save a report through the API; neither operation reruns scanners or calls a model.
10. Optionally configure TAVILY_API_KEY and submit a NEW scan. Inspect actual retrieved
    source URLs/timestamps and execute the bounded follow-up research action. A source
    mention never verifies the sender/offer and does not automatically change risk.

The TCS scenario is also synthetic; it tests a bundled reference-domain match and
negated fees. It does not prove that any real hiring notice or recruiter is authorized.
No offline number, synthetic result, predetermined latency or confidence is an
accuracy benchmark. All displayed current investigation metrics come from backend
calculations and source availability.
