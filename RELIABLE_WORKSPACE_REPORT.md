# Reliable multi-source workspace: changes and preservation evidence

Updated in place on 1 November 2026: `/Users/akshaynaik/Desktop/p1test 2/`.

## Scope and checkpoint

The existing FastAPI/SQLAlchemy services, React/Vite app, dark theme, branding, navigation, existing routes and single-source workflow remain. Existing Cases was extended rather than duplicated. No dependency, LLM/model, database column or migration was added. No existing test or assertion was deleted or weakened. No working feature was disabled to obtain a passing test.

Before editing, Git was clean and `hackathon-working-v1` pointed to `b738fe0a00ba121defcf8693af7081f0811f1965`. The tag and HEAD still point to that same commit. No commit, push, tag mutation or Git-index staging was performed. Existing `.env` and user databases were not used or changed by test setup. Tests use disposable SQLite files; browser validation used ports 8014/5179 and a separate test database.

## Implementation summary and root causes

| Area | Root cause / missing behavior | Incremental change |
|---|---|---|
| Investigator | Chat could read a null top-level organization while the result had canonical structured claims; its separate keyword path could imply unsupported domain risks. | Shared `canonical_context` projects the stored scan/case snapshot without new extraction. Deterministic answers use claims, recorded findings, exact-notice comparisons, recommendations and limitations. Missing fields use plain-language unknowns. Evidence IDs and source citations are returned; answers show their snapshot revision. Existing `/ai/investigate` remains, and Cases adds a case-scoped Investigator. |
| Fee policy | Same-category payment/exemption overlap lacked explicit notice/stage/condition/applicant-scope comparison. | Add `fee_policy_rule` claims with exact excerpts, normalized categories, fee type, stage, condition and notice anchor. Different conditions/stages are context-dependent; different exact notices are not comparable. A definite submitted-policy contradiction requires matching explicit scope. Unknown scope is “Possible inconsistency — needs clarification.” This is not an independent fraud conclusion. |
| Multi-source intake | Cases already persisted independent sources and revisions, but required one upload at a time and had no five-image cap. | Add batch multipart intake that composes existing ingestion services. Optional URL/message/sender/organization fields and multiple files share one case. Missing types are skipped. Maximum five active screenshots is checked in batch and existing backend routes, and both frontend forms. URL/PDF caps default to ten each and are configurable; the existing total cap is 25. |
| Partial processing | URL structure may be processed while page retrieval is unavailable; a summary count alone could obscure that distinction. | Source cards label partially processed/unavailable/review-required states. Summary separately counts analyzed, partial, failed and awaiting-review sources. Failed sources are retained with reasons; successful sources continue. |
| File selection | A deferred React state update could read the file input after it had been cleared. | Capture selected File objects before resetting the input, preserving the selection across repeated/multiple uploads. Browser PDF selection, submit and review were successfully exercised after this fix. |
| Unified report | Only single-scan PDF export existed. | Add an owned case PDF endpoint exporting the current stored sources/statuses, claims, both comparison excerpts, exact-notice results, evidence, limitations and next checks. Existing single-scan reports remain unchanged except for the additive case-section hook. |
| Exact-notice configuration | Official-document retrieval shared the arbitrary case-URL fetch switch. | Add `OFFICIAL_NOTICE_FETCH_ENABLED=false` as a separate opt-in for existing trusted-domain exact-notice retrieval. `CASE_URL_FETCH_ENABLED` retains its behavior. Trusted-host boundaries, public IP validation, pinned TLS, redirects, size/time limits and research budgets remain. A manual field-comparison table is available when retrieval cannot run. |
| TrustGraph | Every record was fit into the initial view, making long PDFs tiny. | Keep React Flow; default to a compact projection grouped by record type. Expand a group/all records, collapse, pan/zoom/fit, inspect nodes/edges and browse every original record/relationship. Grouping never invents relationships or changes underlying evidence. The six-source demo shows 11 overview nodes instead of 30 original records. |

The existing stipend/fee distinction, explicit base/GST-total relation, service liability handling, credential direction rules, duplicate-aware fusion and heuristic/verification separation remain. The original BEL PDF regression still passes: zero critical findings, Undetermined, contractual liability separated, normal credentials not theft. Its EWS overlap is now explicitly a possible inconsistency when scope cannot be established. No claim that this original notice is authentic was made.

## Completed behavior

- Existing Cases accepts any supported single source or optional mixtures in one case; sources retain IDs, filename/URL metadata, timestamps, processing states, original reviewed text, claims and provenance.
- URL/text are scanned directly. PDFs/images retain the existing mandatory UI review/correction step. “Analyze All Evidence” extracts uploaded files and visibly requests review; it does not bypass human review or pretend extraction is verification.
- Add evidence later, remove sources, retain revisions, recompute comparisons/fusion/graph and exclude duplicates from additional confidence/coverage.
- Case and scan chat read canonical stored data and remain deterministic without paid APIs or local models.
- Fee scope is conservative; direct personal-account payments and outward password/OTP requests retain strong warnings. Unclear monetary relationships are not guessed.
- Exact-notice action can be enabled for trusted-host retrieval independently of arbitrary URL page fetching. Missing keys, disabled retrieval, mismatched notices and unavailable providers remain unresolved, with manual comparison steps.
- Unified case PDF export and existing single-scan exports work through their separate retained routes.

## Actual validation results

| Check | Baseline before edits | Final |
|---|---|---|
| Backend full suite with original BEL PDF enabled | 297 passed, 0 failed, 0 skipped | **325 passed, 0 failed, 0 skipped**, 12.26 s |
| Frontend logic suite | 12 passed, 0 failed | **15 passed, 0 failed** |
| TypeScript and Vite production build | Passed | Passed; 3,095 modules |
| Existing labelled synthetic benchmark | Existing regression suite | 45/45 scenarios passed |
| Focused first-stage regression | — | 68 passed before subsequent changes |
| Existing suite after intake/API changes | — | 297 passed before adding new tests |
| Whitespace errors / checkpoint | Clean baseline | `git diff --check` passed; tag unchanged |

One inherited FastAPI/Starlette TestClient deprecation warning and the inherited main bundle-size warning remain. An intermediate graph TypeScript failure was corrected before proceeding; the final build passes. No final failing test remains.

The 28 added backend cases cover all ten requested optional input combinations, five/six screenshot boundaries through both intake routes, partial URL failure, invalid uploaded bytes despite claimed MIME, configurable limits, stale revisions, case isolation, later additions, duplicate confidence/revision preservation, owner/unauthenticated access to new routes, canonical scan/case organization handling, missing/null fields, real evidence citations, case PDF export, category/exemption ambiguity, same-scope contradiction, different conditions, optional sender classification and the dedicated official-only switch. Existing tests retain the stipend/fee, tax total, service penalty, screenshot OCR, exact-notice mismatch, SSRF, action/fusion/graph and security regressions.

Three added frontend logic tests cover optional source validation/image limits, configurable limits and honest source-status labels, and graph grouping/expansion/state preservation over 100 claims. Browser checks supply additional workflow evidence rather than treating a successful build as preservation proof.

### Browser/API demonstration actually executed

A synthetic Acme Labs Data Intern case was created through `/cases`. One URL and a ₹999 personal-account message were submitted together through the new browser form. A PDF and three screenshots were then added to this same case through the real batch API. Native Tesseract extracted all three images; extracted PDF/image text was submitted unchanged through the real review API.

The result retained six sources, one duplicate, the ₹45,000/₹30,000 stipend disagreement and the explicit no-registration-fee versus payment disagreement, with citations to the original sources. The URL was partially processed: URL structure scanned, page extraction unavailable because retrieval was disabled. The assessment was Elevated concern with unresolved authenticity, not a verified fraud verdict. Heuristic scores are not accuracy measurements.

The browser verified canonical “Acme Labs” chat with a recorded snapshot revision; graph expansion from 11 to 30 nodes and back; and the preserved navigation/theme. A further PDF was selected through the actual browser file control, submitted, reviewed and investigated through the UI, then removed through the source card. Source counts changed 6 → 7 → 6 while revisions/history remained. File chooser automation stalled on its first attempt; selection, submission, review and removal subsequently succeeded. Multi-image selection itself was validated through API tests and native OCR, not through another browser chooser attempt.

At a 390×844 responsive breakpoint, intake fields stacked and navigation collapsed. Measured viewport/document widths were both 382 CSS pixels, with no horizontal document overflow. This is a narrow-screen smoke check, not certification of every page/device. Temporary viewport overrides were reset.

### Synthetic benchmark metrics

45 synthetic development scenarios: concern TP 16, FP 0, FN 0, TN 29; precision/recall 100%, false-positive rate 0%, abstention 29/45 = 64.44%. Focused extraction: 46 annotated true positives, zero false positives/negatives, precision/recall 100% within the declared annotation scope.

These figures are regression measurements, **not real-world accuracy**, a held-out evaluation or calibrated probabilities. Labels and rules were developed together; unannotated fields are not exhaustively scored. An abstention/negative is not proof of authenticity. OCR-noise benchmark cases replay transcripts; the separate real image pipeline was exercised in the full suite and six-source demonstration.

## Feature-preservation checklist

“Passed” below refers to the stated test boundary, not a claim that every possible UI path is certified.

| Existing feature | Evidence in this validation | Status / limits |
|---|---|---|
| Single-source text analysis | Full API/scanner/payment/integrity suite, real scan chat regression | Passed; no case required |
| Single-source URL analysis | Existing URL API tests, unavailable-network semantics, SSRF tests | Passed offline; live providers not tested |
| Single-source PDF analysis | Original 16-page BEL binary regression and malformed PDF tests | Passed |
| Single-source screenshot analysis | Native OCR/review regression, correction and failure tests | Passed; OCR remains imperfect |
| Multi-source Cases | New combinations, review, later additions, removal/revisions, duplicate/isolation tests plus six-source native demonstration | Passed |
| Authentication / authorization | Existing register/login/me/ownership/admin tests plus unauthenticated/foreign-owner tests for all new case endpoints | Passed at API level; no production identity-provider test |
| Dashboard | Existing metrics API tests on stored scans | Passed API; full browser charts not retested |
| History / saved scans | Stored-read, legacy integrity, revision-history and snapshot tests | Passed API; no destructive migration performed |
| Comparison | Existing `/compare` tests retain conservative authenticity semantics | Passed API |
| Community | Existing list/create flow on disposable records | Passed API; full browser voting flow not retested |
| Browser extension | Extension files and routes were not edited | **Installation/background/content-script integration not tested** |
| Trust Passport | Existing generation/API integrity tests | Passed API; QR handoff in another device not tested |
| AI Investigator | Existing route plus canonical organization, no-null, missing-domain and citation tests; browser case chat | Passed deterministic mode; no live LLM adapter tested |
| TrustGraph | Existing layout/provenance tests, new grouping test, browser compact/expand interaction | Passed; all original node/edge lists remain |
| Next Best Investigation | Existing sender action, exact-notice success/failure mocks, idempotence/budget/revision/fusion tests | Passed offline; live Tavily retrieval not tested |
| Downloadable scan PDF / saved reports | Existing report save/retrieve/PDF suite | Passed API |
| Unified case PDF | New export test plus actual six-source export text/content checks | Passed API; arbitrary large report visual layout not exhaustively certified |
| Emergency recovery | Existing money-sent and password-entered guidance API tests | Passed API; real banking/recovery actions not performed |
| Input validation, redaction, SSRF and rate limits | Existing security, ownership, upload signature/size, pinned-host, redirect/private-IP and throttling regressions | Passed tested boundaries; no full penetration test |
| Theme/navigation/routes | Existing router/navigation files retained; browser Cases/summary/mobile checks | Targeted smoke passed; every historical page not manually visited |

## API compatibility and configuration

Existing endpoints and required fields remain. New routes:

- `POST /api/cases/{case_id}/sources/batch`: multipart `payload` JSON `{expected_revision, sources:[{input_type,content,title?}]}` plus repeated `files`. Every field/type can be absent individually, but at least one source is required. No client MIME value is sufficient to authorize a file; existing byte validation still runs.
- `POST /api/cases/{case_id}/investigate`: `{question}`. Uses the latest owned case snapshot.
- `GET /api/cases/{case_id}/report/pdf`: exports the current owned stored case without rescanning.

Responses add `source_limits`, `fee_policy_rule` claims, chat `citations`/`context_revision`, and manual exact-notice comparison metadata. Existing response keys are retained. Source lifecycle codes remain compatible; clearer labels are a frontend projection. Archived snapshots are not rewritten. Old scans/cases remain readable; reprocess evidence to obtain new contextual findings. No migration beyond existing `0002_multi_source_cases` is required.

`CASE_MAX_URLS=10` and `CASE_MAX_PDFS=10` are the defaults; total active sources remain 25 and screenshots are capped at five. `OFFICIAL_NOTICE_FETCH_ENABLED=true` allows only the existing bounded official-host exact-notice action; it still needs a trusted organization reference, unambiguous notice identifiers, Tavily and remaining budget. It does not turn on arbitrary case page retrieval. `CASE_URL_FETCH_ENABLED` retains its existing behavior and remains false by default. No existing `.env` was changed or key installed. Manual comparison remains available without any provider.

## Exact macOS run commands

These use the Python runtime and frontend dependencies already present on this machine. Preserve the existing `.env` and use the same chosen database/working directory as before.

Terminal 1:

```sh
cd "/Users/akshaynaik/Desktop/p1test 2/backend"
source "/Users/akshaynaik/Documents/Codex/2026-11-01/do-not-make-gemma-or-any/work/venv/bin/activate"
# Existing migration only; no new migration was added by this change.
alembic upgrade head
AI_PROVIDER=none uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```sh
cd "/Users/akshaynaik/Desktop/p1test 2/frontend"
npm run dev
```

Open `http://localhost:5173/cases`; single-source analysis stays at `/analyze`. Restart running services to load backend code. No Gemma/Ollama or LLM API is required. An existing relative SQLite URL resolves against the backend working directory; keep it consistent rather than accidentally selecting the other inherited database.

Tests from project root with the same Python environment active:

```sh
BEL_REGRESSION_PDF='/Users/akshaynaik/Downloads/Vacancy for  BE  In BEL.pdf' python -m pytest tests -q -p no:cacheprovider
cd backend
python evaluate_accuracy.py --output /tmp/fake-or-real-benchmark.json
cd ../frontend
node --experimental-strip-types --test tests/*.test.ts
npm run build
```

Without the optional original-PDF path, that one binary regression explicitly skips. Other portable synthetic/native-image regressions remain available. The original PDF hash is checked before asserting its output.

## Demo walkthrough

Use the clearly labelled fixtures in `outputs/reliable-workspace-demo/` delivered with this report. They are synthetic, not real recruitment evidence.

1. Create a case named “Synthetic demo — Data internship”. Click Add Evidence.
2. Paste `https://example.com/jobs` and the contents of `message.txt`. Select `synthetic-notice.pdf` and the three PNGs. All belong to this one synthetic opportunity.
3. Click Analyze All Evidence. URL/message process directly; files expose extracted text for review. If URL retrieval is disabled, its structure is analyzed and page content is explicitly unavailable. Nothing marks that page verified.
4. Review/correct each PDF/image source and click Investigate reviewed text. Expected cited observations: ₹45,000 versus ₹30,000 monthly stipend, separate ₹999 personal-account demand, one repeated poster copy. No stipend is used as the fee amount.
5. Inspect source excerpts, grouped findings, unknowns and compact graph. Expand all records or an individual group; click nodes/edges or the original-record lists for provenance.
6. Ask the Investigator “Is this company genuine?” and “Why is this fee risky?” It uses the current case snapshot; Acme Labs is a submitted identity, not authenticated.
7. Download the unified report. Add/remove a source and inspect an earlier revision.
8. Repeat with URL blank, or with only text. The absent type is skipped; it does not become a failure or safety signal. The automated suite tests every requested missing-type combination.

## Safety and accuracy boundaries / remaining work

- All scoring and evidence remain deterministic. Optional provider-independent LLM infrastructure is preserved; no model was installed and no LLM independently determines risk or invents evidence.
- Submitted agreement, company existence, trusted-domain reference, retrieved context, exact-field corroboration, file authenticity and recruiter/payment authorization remain separate. The current original BEL notice has not been independently authenticated.
- Scope extraction is deliberately conservative and pattern based. Complex legal conditions, long-range references, multilingual/OCR-damaged tables, multiple roles or candidate subcategories can remain unresolved or be missed. Different condition strings are treated as context-dependent rather than aggressively contradicted; paraphrased equal conditions may need manual comparison.
- Existing general submitted-claim comparisons remain; they describe disagreement, not which source is authentic. Exact official-notice comparisons retain stricter anchor/trusted-origin gates. No blanket company or gateway allowlist suppresses harmful payment/credential requests.
- Deduplication groups exact content and rule-derived payment facts; source independence is not established merely by uploading multiple copies. Perceptual image similarity or universal paraphrase matching is not implemented.
- Live Tavily/official-host retrieval and external threat providers were not exercised with real keys. Mock contracts, domain boundaries, failure paths and budgets passed. The official-only switch is a configuration option, not automatic permission to contact arbitrary hosts.
- Batch work is sequential/request-time, not a durable background queue. Worker crash recovery, transactional whole-batch retry and very large reports remain limitations. Valid source failures are retained and successful sources continue; stale/concurrent revision conflicts require reload.
- File text review remains per source. There is no unreviewed “analyze every uploaded image automatically” shortcut, old-scan import into a case, source reordering or new persistent original-file archive. Existing direct single-source compatibility routes remain.
- The browser test exercised PDF file selection/upload/review and source removal; three-image intake and native OCR were exercised via API. Arbitrary browsers, mobile file choosers, extension installation, all historical pages, PostgreSQL/Docker and production deployment were not certified.
- Existing synchronous parser/OCR limits, retention/erasure policy limitations, chunk size and upstream TestClient warnings remain. No calibrated fraud probabilities or real-world accuracy claim is made.

## Files changed

- `API.md`
- `ARCHITECTURE.md`
- `BUILD_STATUS.md`
- `README.md`
- `RELIABLE_WORKSPACE_REPORT.md`
- `backend/app/api/v1/endpoints/ai_chat.py`
- `backend/app/api/v1/endpoints/cases.py`
- `backend/app/core/config.py`
- `backend/app/schemas/all_schemas.py`
- `backend/app/schemas/cases.py`
- `backend/app/services/ai_investigator.py`
- `backend/app/services/case_assessment.py`
- `backend/app/services/case_claims.py`
- `backend/app/services/case_intake.py`
- `backend/app/services/case_report.py`
- `backend/app/services/case_service.py`
- `backend/app/services/cross_source_service.py`
- `backend/app/services/fee_policy_scope.py`
- `backend/app/services/investigator_context.py`
- `backend/app/services/notice_verification.py`
- `backend/app/services/recruitment_claims.py`
- `backend/app/services/recruitment_consistency.py`
- `backend/app/services/report_generator.py`
- `frontend/src/api/cases.ts`
- `frontend/src/api/client.ts`
- `frontend/src/components/cases/CaseIntake.tsx`
- `frontend/src/components/cases/CaseSourceCard.tsx`
- `frontend/src/components/cases/intakeValidation.ts`
- `frontend/src/components/common/AIInvestigatorModal.tsx`
- `frontend/src/components/common/RecruitmentReview.tsx`
- `frontend/src/components/common/TrustGraph.tsx`
- `frontend/src/components/common/graphOverview.ts`
- `frontend/src/pages/CaseWorkspacePage.tsx`
- `frontend/tests/reliable-workspace.test.ts`
- `tests/test_reliable_workspace.py`

Generated frontend build assets were rebuilt; dependency manifests, authentication/security middleware, extension files, original databases and original PDF were not edited.
