# Limitations and deferred integrations

- Default fusion uses documented heuristic assumptions. Risk, confidence and
  coverage are distinct; none is an accuracy metric or calibrated probability.
  No validated calibration dataset ships. Correlation grouping is conservative
  policy, not a complete dependence model. The legacy weighted Trust Score and
  confidence index are retained for compatibility and are visibly labelled.
- Tavily snippets are retrieved context, not authenticated findings. Official-domain
  classification comes from a bundled reference list, not live corporate registries.
  The adapter does not automatically establish claim support/contradiction, recruiter
  identity or offer authorization. Missing/negative search results do not prove safety.
  Live Tavily was not tested without a user key; mocked contract/failure tests ran.
- No actual local or hosted LLM adapter is bundled. The protocol/registry, validation,
  timeout and deterministic fallback are implemented and tested using test providers.
  Gemma, Ollama and LangChain are intentionally deferred per the user's priority.
  Future provider integration requires real adapter and live-service testing.
- DNS/TLS are optional and disabled by default. Real RDAP/domain-age retrieval is
  absent. VirusTotal and URLhaus remain explicit unavailable adapter placeholders.
  Google Safe Browsing is inherited HTTP code; live-key behavior was not exercised.
- Deterministic rules can misinterpret context, quotations and negation. Payment
  detection now excludes salary-only amounts and simple negated fee statements,
  but broader semantic false positives/negatives remain. Reference matches and
  valid TLS never prove offer legitimacy. Registrable-domain parsing is heuristic,
  not a full Public Suffix List implementation. Static references need maintenance.
- OCR requires native Tesseract. Failure/empty extraction is explicit. PDF extraction
  is text based; scanned PDFs require a separate OCR path. Document editing-tool and
  metadata-date heuristics are weak indicators, not proof of tampering.
- Follow-ups use revision reservations and a finite budget, with no durable job
  queue. A process crash after reservation can leave RUNNING state; recovery/leases
  and production cancellation are pending. Completed actions are not rerunnable;
  create a fresh investigation for a new verification cycle. Synchronous database
  sessions still bound some throughput; multi-worker load was not tested.
- Historical scans lack retained execution provenance. They are shown with unknown
  coverage rather than rescanned on read. New snapshot records preserve full data.
  Original database files are retained untouched. Explicit reanalysis needs a new scan.
- Local demo mode is intentionally a shared environment. Public production requires
  authentication, disabled demo mode, secrets, trusted CORS, TLS termination, parser
  isolation, distributed rate limiting and security review. Password reset/account
  verification UI, some profile/settings pages and the extension contain inherited
  demonstration behavior. They are not represented as complete production services.
- Browser extension and emergency advice are preserved, not comprehensively updated
  or validated against current provider/jurisdiction changes in this upgrade.
- PDF/Trust Passport are evidence summaries, not cryptographic certificates.
  Unicode glyph coverage in the inherited PDF fonts is limited. Frontend keeps its
  existing large main bundle; Vite emits a non-fatal size warning. New TrustGraph
  code is loaded separately. Docker/PostgreSQL deployment has not been smoke tested.
