# Codebase audit — 1 November 2026

The uploaded archive is the existing application; this directory is its extracted,
upgraded copy. The source archive and its databases are preserved. The pasted brief
is reference material. The user's explicit LLM-optional priorities take precedence.

## Verified implementation

- React 19 / TypeScript / Vite frontend, FastAPI / SQLAlchemy backend. README's
  React 18, PyMuPDF, LangChain and registry-query claims do not match implementation.
- Eleven scanner modules implement URL structure, lexical content, payments,
  sensitive requests, organization reference matching, email headers, phone format,
  salary rules, TF-IDF similarity, DNS and TLS. Existing weighted trust scoring and
  deterministic question answering are real code and should be retained.
- PDF extraction uses pypdf. OCR calls Tesseract, but currently invents internship
  text and bounding coordinates if extraction fails. This is a correctness bug.
- Organization data is a static reference list, not live MCA/SEC verification.
  Domain fixtures and TLS fixtures are mixed into normal scans. Unknown domain
  registration dates are fabricated from DNS success. Phone complaints are fixtures.
- Google Safe Browsing has HTTP integration. VirusTotal and URLhaus return CLEAN
  without requests. Demo intelligence runs for every scan, independent of DEMO_MODE.
- Weighted scoring treats absent signals as clean. Confidence has a 60% floor.
  New uncertainty-aware fusion must be separate and explicitly heuristic.
- Analyze persists findings/checks; GET scans, AI chat and PDF regenerate scans,
  potentially producing different evidence and repeated network calls. Recommendations
  and provenance are lost on reload. A persisted investigation snapshot is needed.
- Authentication issues tokens, but /auth/me returns the first user and can create
  an admin. Admin routes lack authentication. Existing scan history is globally
  accessible; production isolation requires explicit authorization.
- JWT has a known default, CORS includes '*', limiter exists but is unused.
  File validation accepts arbitrary RIFF as WebP; uploads are read before size checks.
  SSRF rejects many private destinations, but unresolved hosts are allowed; TLS
  connects after a second DNS resolution. No arbitrary web-page fetching is needed
  for Tavily; provider requests must use a fixed endpoint without redirects.
- Demo, comparison, dashboard, passport and audit views contain hardcoded fallback
  records. These must be labelled or removed from ordinary production paths.
- SQLAlchemy create_all exists; no versioned migrations. Additive tables can retain
  old scans without altering columns. Migration must support an existing database.
- Existing tests: 28 cases across scanners, API and security. Some tests rely on
  public demo endpoints and seeded community data. No frontend test runner.

## Startup and baseline

Backend: `cd backend && uvicorn app.main:app --port 8000`.
Frontend: `cd frontend && npm ci && npm run dev`.
Run backend tests from project root with `python -m pytest tests -q`.
Baseline frontend build succeeds (large bundle warning). Backend baseline results
and final verification are recorded in BUILD_STATUS.md. Tests use a separate database.

## Scope

Implement deterministic investigation orchestration, bounded Tavily research,
heuristic/Bayesian fusion, provenance, NetworkX graph, executable recommendations,
persistence and integrated results UI. Keep LLM explanation/extraction behind a
provider protocol, disabled by default. Do not install/configure Gemma or require
LangChain to run this explicit bounded workflow. No claims of production certification,
calibrated probabilities or live verification without actual evidence.
