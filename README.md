# Latest organization-role and multi-input fixes — 1 November 2026

Primary organizer extraction now distinguishes claimed collaborators and certificate
associations. Disclosed training fees remain unresolved without automatic critical
risk; explicit personal-account/coercive demands retain warnings. Analyze reuses
Cases batch intake for optional mixed sources while keeping single-format tabs.
TrustGraph has measured/resize fitting and a readable program overview. Dashboard
categories are explicitly labelled stored community reports including synthetic demos.

**350 backend tests, 18 frontend tests and the production build passed.** No model,
dependency, migration, commit or push was added. Checkpoint tag is unchanged. See
CRITICAL_MULTI_INPUT_REPORT.md for the before/after Corizo result, root causes,
A–O test coverage, preservation checklist, manual walkthrough and limitations.
Earlier test counts below describe earlier versions. Re-submit old scans for new results.

# Latest reliable-workspace validation — 1 November 2026

Existing Cases now supports batch optional evidence intake, maximum five screenshots,
canonical scan/case Investigator context, contextual fee-policy scope, compact expandable
React Flow and unified case PDF reports. Official-only exact-notice fetching has a
separate opt-in; absent providers stay unresolved. No model or new migration is needed.
**325 backend tests and 15 frontend tests passed; TypeScript/Vite build passed.**
See RELIABLE_WORKSPACE_REPORT.md for the feature-preservation checklist, run commands,
synthetic demo, exact files and limitations. `hackathon-working-v1` is unchanged;
no commit or push was made. Earlier validation counts below are historical.

# FAKE OR REAL — evidence-based investigation

Current accuracy/integrity update: **241 backend tests**, **9 frontend tests**, and
the TypeScript/production build pass. `/challenge` runs three reproducible synthetic
examples through the real case pipeline. The 45-case synthetic benchmark measures
concern/abstention behavior separately from focused extraction; its development-set
results are not real-world accuracy. Normal-looking unverified offers are
Undetermined. No model is required. See ACCURACY_INTEGRITY_REPORT.md for root causes,
metrics, API compatibility changes, exact files and remaining limits. Earlier test
counts below are historical.


The existing React/FastAPI application has been upgraded in place. Deterministic
forensic scanners, bounded Tavily research, Evidence Fusion, TrustGraph and Next
Best Investigation run without an LLM. **No Gemma, Ollama, hosted LLM, GPU or
LangChain dependency is required.** No model has been installed or configured.

## Run locally

Use Python 3.12+ and a recent Node version supported by Vite 8 (Node 22.12+).
Python 3.15.0 and Node 26.3.1 were used for this build; see BUILD_STATUS.md.

From this project directory:

```sh
# Only for first setup; preserve an existing .env.
cp -n .env.example .env
python3 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173/demo` for synthetic scenarios or `/analyze` for your
own content. API documentation is at `http://localhost:8000/docs`. Run the backend
from `backend/` consistently: SQLite's relative path is based on the current
working directory. The archive's two original database files are preserved; use
an absolute `DATABASE_URL` to choose a specific one. Tests use a temporary database.
The additive migration leaves legacy tables and scan history unchanged.

Development defaults intentionally provide a **shared local demo workspace**.
Bind it to loopback. With `DEMO_MODE=false`, authentication and ownership checks
apply. Login/register now issue and use real backend tokens, stored for the browser
session. Production also requires a unique JWT secret of at least 32 characters,
explicit trusted CORS origins, and demo mode disabled. See SECURITY.md.

## What works without configuration

- Existing URL, text, email, organization reference, phone format, payment,
  sensitive-data, salary and similarity rules; PDF parsing; emergency guidance.
- Legacy weighted Trust Score and deterministic investigator are preserved.
- Evidence IDs, original observations, provenance, timestamps and correlation groups.
- Heuristic fusion, independent confidence and coverage, explicit unknowns.
- NetworkX graph shown with React Flow, clickable evidence and source inspection.
- Rule-ranked next checks, local sender-domain comparison, history, revision
  protection and durable updates; saved reports/PDFs read the same stored snapshot.
- An offline judge demo with explicitly synthetic fixture observations.

Native Tesseract is optional for image OCR. Missing OCR now returns an explicit
unavailable/422 result instead of inventing document text. DNS/TLS checks are
optional (`NETWORK_SCANNERS_ENABLED=true`); absent checks remain unknown. Domain
registration age is unknown without real RDAP data. Bundled organization references
are never described as live MCA/SEC verification.

## Optional external research

Set `TAVILY_API_KEY` in the backend environment to enable one initial organization
search and a recommended follow-up search. Each request has a timeout and at most
five sources; an investigation has a hard three-call budget. Only organization
search terms are sent, not full documents. Source title, URL, excerpt, time, relevance
and verification status are stored. A search mention, an official company website,
or no negative results does **not** authenticate a sender or offer. Retrieved search
excerpts are unverified context and do not change risk automatically.

The adapter follows the [Tavily Search API contract](https://docs.tavily.com/documentation/api-reference/endpoint/search).
Live requests require your key and were not exercised in this build; contract and
failure behavior are tested with mock HTTP transports.

## Optional language providers

`AI_PROVIDER=none` is the default. A trusted future adapter implements
`LanguageProvider.understand` and registers through `register_provider`. Local Gemma,
other local models and hosted models use the same contract. Allowed tasks are
content understanding, verbatim claim extraction, summarization and explanation.
The schema rejects risk scores and invented evidence fields. Citations must reference
existing evidence; extracted claims must quote submitted content. Interpretations
remain explicitly unverified and never enter scoring, graph relationships, searches
or evidence storage as facts. Failure, timeout or invalid output returns deterministic
fallback. See AI.md for the extension contract. Provider-specific installation and
LangChain integration are deferred; neither belongs in the core runtime.

## Validate

```sh
python -m pytest tests -q
cd frontend
npm run build
```

The build command runs TypeScript checking and the Vite production build. Unit and
integration tests need no model or API keys. BUILD_STATUS.md records exact results,
migration checks and browser smoke verification. CODEBASE_AUDIT.md distinguishes
working implementations from inherited mocks and remaining limitations.


## Accuracy and usability fixes

The monetary scanner now separates salaries/stipends from local fee/deposit amounts,
retains source spans and refuses ambiguous assignments. Screenshot uploads now use
an OCR preview/correction step before investigation; filenames never become automatic
organization claims. The React Flow graph has semantic columns and an evidence side
panel. The checklist separates verified, failed, warning, unavailable and unperformed
checks and reports unresolved totals. Follow-up checks expose unavailable reasons.

See ACCURACY_USABILITY_REPORT.md for root causes, changed files, test commands and
limits. This update passed 145 backend cases (including real native OCR), four frontend
logic tests, browser smoke checks and the TypeScript/production build. No model is
required. Restart the backend to load code changes if it is not running with reload;
re-submit previously saved scans to correct cached old fee findings.


## Multi-source investigation workspace

Open `/cases` to investigate one opportunity using multiple screenshots, PDFs, URLs,
texts, emails and phone numbers. Cases preserve exact claim citations, per-source
findings, cross-source comparisons, duplicate-aware heuristic fusion, TrustGraph,
next checks and immutable assessment history. Review image/PDF text before scanning.
Removing a source recomputes current findings; older snapshots remain available.
A legitimate-looking poster alone stays UNDETERMINED.

Run `alembic upgrade head` from backend/ before restarting; the additive head is
`0002_multi_source_cases`. No LLM or new dependency is required. Public URL page
fetching is optional (`CASE_URL_FETCH_ENABLED=false` by default); URL structure still
runs through existing scanners. Missing external services remain unresolved.

Latest validation: 187 backend cases passed, 5 frontend logic tests passed, TypeScript
and production build passed. See MULTI_SOURCE_WORKSPACE.md for API, run commands,
exact changed files, migration checks, browser verification and known limitations.


## Context-aware recruitment verification

Application fees, stipends, contractual liabilities and normal account instructions now
retain contextual classifications and exact page references. Repeated payment facts
share one finding. Recruitment results show found claims, distinct concerns, scoped
verification, unknowns and next steps. Exact-advertisement corroboration is optional:
`verify_notice` uses configured Tavily plus `CASE_URL_FETCH_ENABLED=true` to retrieve
bounded full documents on a trusted website; snippets and company existence cannot
verify an offer. The core still runs with no model or external keys.

The original 16-page BEL regression changed from risk index 95/nine critical findings
to Undetermined/zero critical findings. A real EWS fee/exemption inconsistency remains
cited for clarification. The notice was not authenticated. Latest validation: 297
backend tests, 12 frontend logic tests and TypeScript/Vite build passed. See
CONTEXT_AWARE_VERIFICATION_REPORT.md for root causes, exact files, commands and limits.
Earlier validation counts above describe earlier versions.
