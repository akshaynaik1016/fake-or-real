# Current critical accuracy/multi-input validation — 1 November 2026

Baseline: 325 backend tests, 15 frontend tests, production build passed.
Final: **350 backend tests passed (0 failed/skipped), 18 frontend tests passed,
TypeScript/Vite production build passed**. Original BEL binary regression enabled.
Existing 45 synthetic benchmark scenarios passed; not real-world accuracy.

The supplied Corizo reconstruction selects Corizo, not Microsoft; training fee is
unpriced/moderate, checklist has zero failures, offer/partnership verification remains
unresolved. Analyze-to-Cases combined text/URL, case chat/report, graph visibility,
all-record expansion, resize and dashboard source labels were browser/API checked.
No security protection, existing feature or old assertion was removed. No LLM,
dependency, migration, commit or push; hackathon-working-v1 is unchanged.
See CRITICAL_MULTI_INPUT_REPORT.md for exact test boundaries and remaining limitations.

Earlier records are historical.

---

# Reliable workspace validation — 1 November 2026

Baseline: 297 backend / 12 frontend tests and production build passed. Final:
**325 backend / 15 frontend tests passed, 0 failures**, production build passed.
The original BEL PDF regression was enabled. Existing 45-scenario synthetic benchmark
passed; this is development regression coverage, not real-world accuracy.
Browser/API validation covered one case with URL, PDF, message and three screenshots,
native OCR, partial URL availability, canonical chat, compact graph expansion,
subsequent PDF selection/upload/review/removal and a 390px responsive smoke check.

No feature was removed, no old test was weakened, no dependency/migration/LLM was
added and no Git commit/push was made. Tag hackathon-working-v1 remains at
b738fe0a00ba121defcf8693af7081f0811f1965. Live external providers, installed extension,
all historical UI flows and production deployment were not tested. See
RELIABLE_WORKSPACE_REPORT.md for the preservation checklist and exact test boundaries.

Earlier records follow as historical context.

---

# Current context-aware recruitment validation — 1 November 2026

**297 backend tests passed, 0 failed, 0 skipped**, with the exact original BEL PDF
regression enabled. **12 frontend logic tests passed**; TypeScript/Vite production
build passed (3,092 modules). The inherited TestClient deprecation and bundle-size
warning remain. The existing 45-example synthetic benchmark still passes; its results
are development regressions, not real-world accuracy.

The original PDF failure was reproduced at risk index 95/nine critical findings.
The updated real PDF API and browser show Undetermined/zero critical findings, one
grouped unresolved application-fee observation and one cited moderate EWS fee-scope
inconsistency. Contract liability and normal account instructions are distinguished.
PDF report export passed content checks. No exact advertisement authenticity claim
was established; independent retrieval success/failure was tested with mock transports.

No model, dependency or database migration was added. Existing project, .env and user
databases were preserved. See CONTEXT_AWARE_VERIFICATION_REPORT.md for exact files,
commands, benchmark limits, provenance and remaining failure modes. Earlier validation
records below are historical.

---

# Current accuracy/integrity validation — 1 November 2026

**241 backend tests passed, 0 failed, 0 skipped. Nine frontend logic tests passed.**
TypeScript/Vite production build passed (3,090 modules). One existing upstream
TestClient deprecation and the inherited bundle-size warning remain. Native AEXON
TECH screenshot OCR/review/provenance passed. Browser verified all three Evidence
Challenge scenarios, preserved case/single-scan views and actual saved-scan comparison.

The offline synthetic benchmark passed 45/45: concern precision/recall 100%, FPR 0%,
abstention 29/45 (64.44%); focused extraction precision/recall 100% over 46 annotated
claim instances. These are development-set regression results, not real-world
accuracy, independent holdout performance or calibrated probabilities.

No LLM/model or new dependency is required; no schema migration was added. See
ACCURACY_INTEGRITY_REPORT.md for audit traces, exact files, compatibility changes,
run commands and known failure modes. Earlier validations below are historical.

---

# Current multi-source workspace validation

Updated in place on 1 November 2026. **187 backend cases passed, 0 failed**, with
one existing upstream TestClient deprecation warning. **5 frontend logic tests
passed**. TypeScript and Vite build passed (3,088 modules; inherited bundle-size
warning remains). All A–G case API scenarios pass. Browser smoke verified a real
case, cited stipend and channel conflicts, ₹999 fee evidence, sender-check execution,
fusion/graph updates, read-only revision history and source removal/recomputation.

Migration and repeat migration passed on a disposable copy reconstructed to pre-case
schema: all 17 existing tables retained identical row hashes/counts, including 28
scan rows; five case tables added at `0002_multi_source_cases`. No live Tavily or
public URL retrieval, production/PostgreSQL or small-screen browser test is claimed.
See MULTI_SOURCE_WORKSPACE.md for exact commands, changes, setup and limitations.

Earlier validation records follow as historical context.

---

# Current accuracy/usability validation

The existing Desktop/p1test 2 project is updated in place. Latest checks: **145 backend
cases passed, 0 failed, 0 skipped**; **4 frontend logic tests passed**; TypeScript and
production build passed. A real native Tesseract → review → forensic scan passed,
and the browser confirmed corrected monetary roles, graph/side-panel interaction,
checklist states, persisted follow-up evidence and fusion updates. No LLM is required.
See ACCURACY_USABILITY_REPORT.md for commands, root causes, exact files and limits.

The previous upgrade validation is retained below as historical context.

---

# Build status — 1 November 2026

**Core investigation workflow implemented and tested with no LLM or API keys.**
No Gemma/Ollama model, hosted-model SDK or LangChain dependency was installed.
The provider-independent interface is implemented; provider-specific adapters remain
future integration work, as requested. The source archive was upgraded in place
inside its extracted project directory; no replacement application was built.

## Validation actually executed

| Check | Command | Result |
|---|---|---|
| Original backend baseline | `python -m pytest tests -q` | 28 passed, 2 warnings, 68.29 s |
| Final backend regression | `python -m pytest tests -q` | 84 passed, 1 warning, 2.72 s |
| Frontend type check + build | `cd frontend && npm run build` | Passed; 3,081 modules transformed |
| Python dependencies | `pip check` | No broken requirements |
| Syntax | `python -m compileall -q backend/app` | Passed |
| Existing DB migration | `alembic -c backend/alembic.ini upgrade head` on a copy | Passed; all 23 original backend scan rows retained |
| Migration idempotence/history | Included regression test | Passed; repeat upgrade retains legacy row and revision |
| Offline browser smoke | Local Vite + isolated SQLite/API | Demo submission, results, graph provenance, follow-up action and persisted revision verified |
| Original data/tests integrity | Byte comparison against uploaded ZIP | Both databases and all 3 original test files unchanged |

Environment: macOS arm64, Python 3.15.0, Node 26.3.1, npm 11.16.0, Vite 8.3.5.
Python package versions are recorded in backend/requirements-tested.txt (environment
snapshot, not a cross-platform lock). Frontend package-lock.json is updated.
Raw validation output is under verification/. The remaining backend warning is an
upstream FastAPI/Starlette TestClient deprecation about httpx. Vite warns that the
inherited main bundle exceeds 500 kB; the new TrustGraph is a separate lazy chunk.
No calibrated accuracy, production certification, live-key research or Docker run
is claimed.

## Completed phases and modified areas

1. **Audit/baseline:** CODEBASE_AUDIT.md and IMPLEMENTATION_PLAN.md identify real
   scanners, inherited fixtures, fake provider responses and security gaps.
2. **Correctness/security:** config, access/auth, rate limiting, document validation,
   OCR fallback, domain age, TLS destination pinning, redaction, provider availability,
   dashboard/admin/history/passport error handling. No fake CLEAN or fabricated OCR.
3. **Core intelligence:** new evidence contracts, Tavily adapter, language protocol,
   explicit orchestrator, independently testable fusion, NetworkX graph, rule-ranked
   recommendations and bounded executable actions. LLM outputs cannot affect scoring.
4. **Persistence/API:** additive migration, investigation snapshots/history and
   endpoints, atomic revision reservations, stored reads for scans/chat/reports/
   comparison/passports. Full old scan history preserved, with honest unknown states.
5. **Results/demo/docs:** integrated React Flow, source/evidence inspection, risk/
   confidence/coverage, next actions/change explanations, explicit provider states,
   synthetic labels, PDF fusion content, setup/security/privacy/limitations guidance.

See CHANGELOG.md for the exact changed/added source file list.

## Run

Follow README.md for isolated Python installation and `npm ci`. Run from backend/:
`alembic upgrade head`, then `uvicorn app.main:app --host 127.0.0.1 --port 8000`.
Run `npm run dev` in frontend/. Open `/demo` or `/analyze`. Default AI_PROVIDER=none
and absent Tavily configuration are fully supported.

## Remaining limitations

Live Tavily and Google Safe Browsing need credentials and were tested only with
mocks/inherited code, not live keys. External search excerpts remain unverified and
do not automatically reduce/increase risk. Gemma/local/hosted adapters and LangChain
are deferred. Calibrated likelihood data, live RDAP, real VirusTotal/URLhaus adapters,
durable execution crash recovery, complete account recovery/profile/settings flows,
distributed throttling, parser isolation, PostgreSQL/Docker smoke tests and production
security review remain pending. See LIMITATIONS.md for practical boundaries.
