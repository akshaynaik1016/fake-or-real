# Accuracy, evidence integrity and Evidence Challenge

Implemented in place in `/Users/akshaynaik/Desktop/p1test 2` on 1 November 2026. The existing FastAPI/React application, source processing, case persistence, TrustGraph, fusion, executable Next Best Investigation and deterministic investigator remain. No new model, mandatory LLM, dependency installation or database schema change was introduced. Existing Alembic head remains `0002_multi_source_cases`.

## Outcomes

AEXON TECH is extracted from a distinctive business heading as a **claimed** organization, with the exact text span. It is not added to the bundled reference registry or declared genuine. Normal-looking content abstains: **Undetermined**, no numeric trust/safety verdict, and specific offer authenticity unresolved. Explicit concerns are **Elevated concern**, while offer verification remains separate. Content rules report completion, never independent authenticity verification. Missing/failed/skipped research stays unresolved. Search success means context was retrieved, not that an offer was authenticated.

Structured claims now appear in single-source investigations as well as cases, carrying source ID, claim type/value, exact excerpt/offsets, method and CLAIMED status. Urgency and observed domains join the existing opportunity, compensation, fees, recruiter, contact, application-channel and sensitive-request fields. Source-level findings retain exact scanner spans where available. Derived comparisons cite all original sources. A rule result without an original captured span explicitly has no original excerpt rather than manufacturing a quotation.

## Audit findings and traces

| Reported failure | Root cause found in this checkout | Change and validation |
|---|---|---|
| AEXON TECH not identified | OCR text reaches scanners, but organization identification only looked for aliases in eight bundled reference organizations. Unknown business names were dropped before entities, research and rendering. | Separate name extraction from reference lookup. Explicit company labels and conservative business headings yield unverified claims with original offsets. Native image → actual Tesseract → review API → scan successfully extracted AEXON TECH; an unrelated Google filename did not become a company claim. |
| Poster produces 100/100 LOW RISK | The legacy scoring baseline starts at 100 with no findings. Result gauge/history/passport/dashboard still consumed it. RiskBadge defaulted unrecognized states to green LOW RISK. Single-source fusion also allowed multiple reassuring groups to yield a low classification; the previous guard was case-only. | Shared assessment semantics abstain without a qualifying concern. API presentation exposes null legacy-compatible trust index when undetermined and an explicit assessment object. RiskBadge defaults to Undetermined; numeric primary displays use a concern index only when appropriate. Case listings/revisions use the same state even when the internal numeric fusion band is MODERATE. Tests cover all actual consumer APIs and browser results. |
| ₹45,000 reported as fee | **Not reproduced in the current checkout.** The preceding context-aware monetary fix is already active: baseline reproduction classified ₹45,000 as stipend and ₹999 as registration fee. Old saved findings are not rescanned on read. | Preserve that parser and extend mixed-amount/order/ambiguity benchmark coverage. Challenge B executes the real pipeline and shows stipend 45000/month separately from fee 999. A new zero-fee regression exposed language rules treating a fee of 0 as a demand; fixed that path and excluded zero amounts from fee claims. |
| Completed checks appear independently verified | Payment/identity/document processing used status `verified`; historic `passed` was promoted to verified. Graph reference edges used VERIFIED and evidence cards showed a green “verified” badge for bundled-reference observations. | Introduce completed status and conservatively project old passed/verified content checks to completed. Completed rules remain unresolved for authenticity. Reference edges are OBSERVED and cards say Reference observation. The separate scoped independent-claim contract requires an externally sourced verification record linked to an existing extracted claim; no current content/reference/search adapter creates it. |
| Research unavailable confused with verification | Adapter already returned SEARCH_UNAVAILABLE for missing keys/failures. Surrounding verification counts, success terminology and a generic skipped-research reason could obscure what actually ran. | Clear unresolved labels for unavailable/not-performed research; successful searches labelled retrieved context. Skipped source research explicitly says it was not requested. Timeout and unconfigured conditions are exercised through the real Tavily adapter with offline fault injection; no search success is fabricated. |

Additional false-positive causes found: the email scanner treated generic HR display names using personal email as critical enterprise impersonation; bundled domain non-matches implied critical wrongdoing; sensitive-document rules treated mentions/advice as requests; payment identifiers alone were high/critical despite lacking a demand. These now remain contextual observations unless affirmative harm indicators support escalation. Explicit brand-lookalike URLs and real fee/credential demands remain concerns. A personal address, DM application, differing recruiter domains or pasted authentication-pass headers never independently authenticate or condemn an offer.

## Assessment and evidence contract

- `assessment.state`: ELEVATED_CONCERN or UNDETERMINED. This is independent from `assessment.verification_status` and `assessment.offer_authenticity`.
- `verification_status`: UNRESOLVED unless a scoped, independently sourced record links to an existing claim. The supported positive contract is INDEPENDENTLY_VERIFIED_CLAIM, restricted to listed claim IDs and scopes. It never promotes the whole opportunity to authentic. The positive contract is unit-tested; no live independent offer-verification adapter is claimed.
- `risk_score`: heuristic concern index, higher means more concern; null for Undetermined. Reliability/confidence indices use `/100`, with explicit uncalibrated wording. Coverage measures performed investigation work, not authenticity or OCR confidence.
- Source claim locations refer to stored redacted/extracted/reviewed text. No filename-derived identity, invented missing period, guessed OCR correction or fabricated evidence is introduced.
- Independently retrieved snippets are EXTERNAL_SOURCE / INDEPENDENTLY_RETRIEVED_CONTEXT and remain unverified. Submitted claims and observed material are separate from retrieval and rule output.
- Existing correlation groups and normalized-content duplicate detection remain. Contradictions compare cited claims; missing fields are unresolved, newly mentioned fees are new information, repeated agreement is supporting claims rather than independent proof.
- Historical stored records and revision snapshots are not rewritten. Read-time integrity presentation can abstain or relabel historical completion using retained evidence. Previously missed extraction or incorrect archived amount findings require a fresh scan/review, not an invented correction.

Compatibility note: primary scan responses retain field names but `trust_score` is now nullable, `risk_level` presents ELEVATED CONCERN / UNDETERMINED, and `analysis_confidence` uses the fusion reliability index. For a concern, the deprecated trust field is the inverse concern index for existing consumers; UI labels display the concern index. Raw legacy scores remain in stored baseline data for audit. Consumers should use the explicit `assessment` object. Check status `completed` is new. Scan listings, passports, dashboard, comparisons, saved new reports and PDFs use the same presentation. Comparison no longer declares a safer/authentic choice based on a legacy score. The inherited comparison page now compares actual saved scans instead of fabricated feed/registry results. Existing extension simulation is explicitly illustrative, with unqueried age/threat information and no fabricated numeric analysis result.

## Synthetic benchmark and measured results

Dataset: **45 diverse synthetic scenarios**, version 1, checked into `backend/app/evaluation/scenarios.json`. Labels describe observable concern/abstention expectations, not real-world authenticity. Includes reassuring unverified posters, new company names, fees/deposits, stipend/fee ordering, impersonation URLs, missing data, contradictory durations/channels/fees/stipends, duplicates, OCR transcript noise, personal email/DM, negation, ambiguity and provider failure/unavailability.

| Metric | Final measured value | Meaning |
|---|---|---|
| Scenario behavior checks | **45/45 pass** | Expected state, focused extraction, exact provenance, unresolved offer verification and applicable comparisons/duplicates |
| Concern detection precision | **100% (16 TP / 16 escalations)** | Escalated synthetic cases match concern labels; not “scam precision” |
| Concern detection recall | **100% (16/16)** | Abstained positive cases would count as missed concerns |
| False-positive rate | **0% (0/29)** | No negative-labelled example was escalated; those 29 are not declared genuine |
| Abstention rate | **64.44% (29/45)** | Remained Undetermined |
| Expected state agreement | **100% (45/45)** | Agreement with this fixed development set's policy labels |
| Focused extraction precision / recall | **100% / 100%** | Exact multiset matching: 46 annotated claim instances, 0 extra/missing instances within each example's specified claim types |

These are **development-set regression results, not real-world accuracy**. Labels and rules were developed together by the same implementation effort; no independent annotation, unseen holdout, prevalence adjustment, confidence interval or calibrated probability is established. Extraction is scored only in each scenario's declared annotation scope; it is not an exhaustive quality measurement of every extracted type. Negatives mean “abstain,” so TN counts are non-escalations rather than authentic offers. OCR-noise benchmark examples replay transcripts; native image OCR has a separate passing integration test.

First evaluation passed 43/45. One genuine zero-fee false positive was fixed. One erroneous gold annotation assigned `/month` to a sentence without a period; the annotation was corrected to null, with no invented period added to extraction. Initial descriptive results were 94.12% concern precision, 100% recall, 3.45% FPR and 97.83% scoped extraction precision/recall. This is a development/debugging record, not an independent before/after accuracy experiment.

## Validation executed

| Check | Result |
|---|---|
| Before-change backend baseline | 187 passed, 0 failed |
| Final full backend suite | **241 passed, 0 failed, 0 skipped**, including native OCR and all existing case/NBI regressions |
| Frontend logic tests | **9 passed, 0 failed** |
| TypeScript and Vite production build | Passed; 3,090 modules |
| Offline evaluation command | 45/45 scenarios pass; detailed actual claims/citations/metrics saved as JSON |
| Browser, isolated DB/backend and no LLM/provider keys | Challenge A/B/C all ran and displayed PASS; A abstained and extracted AEXON TECH, B showed ₹999 fee, C cited both stipend sources. Preserved workspace/single-source view showed unresolved status and completed content rules. Actual saved-scan comparison showed Undetermined vs Elevated concern without an authenticity verdict. |

The existing upstream FastAPI/Starlette TestClient deprecation warning remains. Vite reports the inherited main bundle above 500 kB. Seven early regression failures reflected old assertions expecting LOW RISK, minimum arbitrary confidence, verified content checks and verified reference edges; those assertions were replaced with explicit uncertainty/scope assertions and expanded coverage. No tests were removed. The original payment/order/provenance, case removal, duplication, OCR errors and action idempotency tests remain passing.

No live Tavily request, live public-page retrieval, real offer authenticity verification, small-screen browser certification, Docker/PostgreSQL or production load/security validation is claimed. Browser tests used ports 8012/5177 and a separate temporary-purpose SQLite file; the user's active app/database were not used for example submissions. Temporary servers are shut down after validation.

## Run and reproduce

Use the existing Python environment. Preserve your `.env`; no model is required.

```sh
cd "/Users/akshaynaik/Desktop/p1test 2/backend"
# Activate the existing Python environment.
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```sh
cd "/Users/akshaynaik/Desktop/p1test 2/frontend"
npm run dev
```

Open `http://localhost:5173/challenge`, or Demo Hub → Evidence Challenge. Run A, B and C; each run creates a separately named synthetic case and links to the existing workspace. Expected results are declared before execution. Actual findings, excerpts, pass/fail and assessment come from persisted case processing, not hardcoded outputs. A/C document text is explicitly replayed as a transcript; the page does not pretend to run OCR. The normal screenshot workflow still runs OCR/review separately.

API additions: `GET /api/challenge/scenarios`; `POST /api/challenge/run/{scenario_id}` for `poster-aexon`, `stipend-fee`, `stipend-conflict`. Existing authentication/ownership rules apply outside the shared local demo. No arbitrary scenario content, external tool or provider fault-injection request is accepted through this endpoint. Offline failure probes are confined to the evaluation runner.

Validation commands:

```sh
# From project root, with the Python environment active:
python -m pytest tests -q -p no:cacheprovider
cd backend
python evaluate_accuracy.py --output /tmp/fake-or-real-benchmark.json
cd ../frontend
node --experimental-strip-types --test tests/*.test.ts
npm run build
```

The benchmark script sets an isolated temporary database, disables live scanners/providers/LLMs, and calls the same persisted case services used by the API. It exits nonzero on a failed scenario, writes metrics and actual results, and deletes its temporary database. Run it in a new process. Existing app `.env` and included databases are not overwritten. No migration beyond the existing head is needed for this change.

## Remaining known failure modes

1. Name extraction is conservative and incomplete. Labelled names and distinctive business headings work; arbitrary unlabelled names, line-broken names, slogans and complex affiliations may be missed or misidentified. OCR-confusable characters remain literal; AEX0N is not silently repaired into AEXON.
2. Regex context is not general language understanding. Nested negation, quoted examples, distant request verbs, third-party reports, fee reimbursement/payment direction and unusual multilingual phrasing can still cause misses or false concerns. Government-ID and personal-channel observations require contextual human review.
3. Stipend comparisons require matching category/currency/period, but cannot fully resolve different roles, dates, tiers or offer versions. A cited contradiction is a disagreement, not independent proof of fraud. Missing units remain missing; ranges can abstain.
4. Duplicate detection uses normalized text equality, not perceptual or semantic similarity. Paraphrases and lightly edited copies may remain separate, although scanner correlation groups limit repeated categories.
5. No current adapter independently verifies recruiter authorization or the specific offer. Bundled domains, TLS, pasted authentication headers and retrieved search context are limited observations. Source research may be skipped intentionally; case research is an explicit action. No unavailable result counts as success.
6. Original uploaded binaries/bounding boxes are not retained by this case feature. Provenance is exact within retained redacted/reviewed text, not a cryptographic original-document chain of custody. Saved prior snapshots cannot acquire missing original spans retroactively.
7. Case processing remains request-time work without durable crash recovery. Soft removals retain audit/history text. Distributed scaling, retention/erasure policy, parser isolation and PostgreSQL need further work, as recorded in the prior workspace report.
8. The benchmark is small, synthetic and development-tested. Its perfect final result must not be advertised as generalization, calibrated confidence or production fraud-detection accuracy. More independent, held-out, multilingual and real-world labelled evaluation is required.

## Files added

```text
ACCURACY_INTEGRITY_REPORT.md
backend/app/api/v1/endpoints/challenge.py
backend/app/evaluation/runner.py
backend/app/evaluation/scenarios.json
backend/app/services/assessment_semantics.py
backend/evaluate_accuracy.py
frontend/src/components/common/assessmentSemantics.ts
frontend/src/pages/EvidenceChallengePage.tsx
frontend/tests/assessment-integrity.test.ts
tests/test_assessment_integrity.py
```

## Files modified

```text
API.md
ARCHITECTURE.md
BUILD_STATUS.md
README.md
backend/app/agents/investigation_orchestrator.py
backend/app/api/v1/api.py
backend/app/api/v1/endpoints/analyze.py
backend/app/api/v1/endpoints/cases.py
backend/app/api/v1/endpoints/compare.py
backend/app/api/v1/endpoints/dashboard.py
backend/app/api/v1/endpoints/scans.py
backend/app/api/v1/endpoints/trust_passport.py
backend/app/scanners/email_scanner.py
backend/app/scanners/org_scanner.py
backend/app/scanners/payment_scanner.py
backend/app/scanners/sensitive_data_scanner.py
backend/app/scanners/text_scanner.py
backend/app/schemas/all_schemas.py
backend/app/schemas/investigation.py
backend/app/services/ai_investigator.py
backend/app/services/bayesian_evidence_engine.py
backend/app/services/case_assessment.py
backend/app/services/case_claims.py
backend/app/services/evidence_service.py
backend/app/services/investigation_execution.py
backend/app/services/investigation_store.py
backend/app/services/report_generator.py
backend/app/services/scan_service.py
backend/app/services/trust_graph_service.py
backend/app/services/verification_service.py
frontend/src/App.tsx
frontend/src/api/cases.ts
frontend/src/api/client.ts
frontend/src/components/common/AIInvestigatorModal.tsx
frontend/src/components/common/EvidenceCard.tsx
frontend/src/components/common/InvestigationPanel.tsx
frontend/src/components/common/RiskBadge.tsx
frontend/src/components/common/TrustPassportModal.tsx
frontend/src/components/common/TrustScoreCircle.tsx
frontend/src/components/common/VerificationChecklist.tsx
frontend/src/components/common/verificationSummary.ts
frontend/src/pages/CaseWorkspacePage.tsx
frontend/src/pages/CasesPage.tsx
frontend/src/pages/ComparePage.tsx
frontend/src/pages/DashboardPage.tsx
frontend/src/pages/DemoPage.tsx
frontend/src/pages/ExtensionPage.tsx
frontend/src/pages/HistoryPage.tsx
frontend/src/pages/LandingPage.tsx
frontend/src/pages/ScanResultPage.tsx
frontend/src/pages/SettingsPage.tsx
frontend/src/pages/TrustPassportPage.tsx
frontend/tests/investigation-ui.test.ts
tests/test_accuracy_regressions.py
tests/test_api.py
tests/test_investigation.py
```

The build regenerated frontend dist/cache output. Dependency manifests, actual `.env`, LLM adapters, existing database tables and migrations were not modified by this update. Exact console output and the synthetic dataset/results accompany the handover report. No private input or credential is included in the synthetic evaluation artifacts.
