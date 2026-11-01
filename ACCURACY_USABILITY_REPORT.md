# Accuracy and usability fixes — FAKE OR REAL

The existing project at `/Users/akshaynaik/Desktop/p1test 2` was modified in place.
No application rebuild, new model dependency or LLM installation was introduced.
The existing scanners, weighted baseline, fusion, React Flow, investigator, reports,
history and emergency features remain. User configuration and live databases were
not used for tests; browser verification used an isolated database and ports.

## Reported payment bug: reproduced, then fixed

Before changes, the supplied test input produced:

```text
Payment request identified (registration fee). Amount: ₹/45000.
```

The scanner extracted both amounts globally, converted them into an unordered set,
and used the first member as the upfront fee. It never linked an amount to its
salary or payment context. Its generic observed-value fallback also copied every
amount, including compensation, into payment evidence. The regex could truncate
plain amounts with more than three digits.

The same input now produces:

| Monetary observation | Classification | Source span (zero-based, end exclusive) |
|---|---|---|
| ₹45,000 per month | Promised stipend, COMPENSATION/STIPEND | amount `[114,121)` |
| ₹999 | Upfront refundable registration fee, PAYMENT/REGISTRATION_FEE | amount `[197,201)` |

Payment evidence reads `Payment request identified (refundable registration fee): ₹999.`
It does not include ₹45,000 in its payment finding or observed value.

Amounts are associated with nearby monetary labels in the same sentence/clause.
Registration, security/refundable deposits, processing/training fees, salary,
stipend, scholarship and other compensation have explicit classifications. ₹,
Rs. and INR, Indian comma grouping, multiple amounts, reverse order, clauses,
negation, zero fees and compensation periods have regression coverage. Ranges,
alternatives and unlinked amounts stay AMBIGUOUS; an unpriced fee finding never
borrows a compensation amount. Exact amount/label offsets and quotes survive API
serialization, evidence normalization, persistence and the frontend evidence cards.
Offsets reference the redacted submitted/reviewed text stored with the scan.

## Root causes and changes by priority

| Priority | Root cause | Change and validation |
|---|---|---|
| Payment | Global unordered amount selection and loss of local context | Contextual monetary entities, stable order, explicit roles, exact spans; pure scanner and complete API tests |
| TrustGraph | Index-based four-column grid, full-paragraph labels, labels on every edge and no relation state | Identity left, related entities middle, two evidence lanes right; compact labels; selection highlighting; smooth routes; desktop details panel; observed/claimed/reference-verified/contradicted/unresolved states; deterministic edge IDs and duplicate research-edge prevention; unit/API/browser tests |
| Checklist | Only passed/failed/warning states; all non-passed checks lumped into attention count | Separate verified/failed/warning/unavailable/not_performed, honest check scopes and unresolved summary; scoped verified checks do not authenticate an offer; unit/API/browser tests |
| Investigate Next | Existing reservation/idempotency flow needed end-to-end verification; unavailable errors were generic; checklist did not reflect sender comparison | Actual sender-reference check adds one provenance-bearing finding, recalculates fusion, rebuilds graph, persists revision/history, updates checklist; completed action is idempotent; exact unavailable reasons exposed; repeat execution/API and browser tests |
| Screenshot analysis | Filename forwarded as target organization; all OCR failures collapsed into an unavailable/empty result; no review step | Filename retained only as metadata; real extracted text reaches existing scanners; explicit empty/missing-engine/invalid-image/timeout/engine-error codes; extraction-only preview followed by editable reviewed submission; original direct screenshot/image API retained; PDF filename fallback also removed; mocked and native OCR/API/browser tests |
| Error/progress UX | Structured OCR errors rendered as object strings; animated sequence implied completed external checks | Stage/code/message rendered clearly; scanner errors distinguished from OCR errors; pending UI says it is awaiting backend results |

## What was executed

Baseline on this folder: **84 passed, 0 failed**, 1 upstream warning (3.49 seconds).

Final backend: **145 passed, 0 failed, 0 skipped**, 1 upstream warning (3.33 seconds).
The 61 added parameterized cases are in `tests/test_accuracy_regressions.py`.
No original backend test file or assertion was deleted or weakened.

Command, from the existing project root, using an isolated installed environment:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/akshaynaik/Documents/Codex/2026-11-01/do-not-make-gemma-or-any/work/venv/bin/python -m pytest tests -q -p no:cacheprovider
```

The test configuration uses a temporary SQLite database and disables external
providers. It does not read/write the running application's investigation history.

Frontend logic tests: **4 passed, 0 failed**:

```sh
cd frontend
node --experimental-strip-types --test tests/investigation-ui.test.ts
```

Frontend TypeScript check and production build: **passed**, 3,084 modules transformed:

```sh
npm run build
```

Native Tesseract was present. An actual generated image containing INR 45,000/month
and INR 999 was decoded, OCR'd, reviewed and passed through the real forensic
scanners; the native end-to-end test passed. Mocked tests additionally cover OCR
empty results, missing engine, timeout, internal failure, corrected text, invalid
review tokens and scanner errors. On machines without Tesseract, that one native
test explicitly skips; the mocked pipeline tests still run.

Browser checks, against isolated localhost services, verified:

1. Screenshot investigation is disabled before extraction/review.
2. Real OCR populates an editable preview. The sample's rupee glyph was misread
   as `%`, demonstrating why correction is necessary; it was corrected before scan.
3. The exact supplied text can be entered in the preview and investigated. The
   result shows ₹45,000/month as stipend and ₹999 as the registration fee.
4. Filename does not become the claimed organization. Microsoft comes from text.
5. Clicking Investigate Next changes revision 1 to 2, adds one actual mismatch
   finding, changes the heuristic risk index from 91 to 96, expands the graph and
   changes the checklist summary. These are this test run's computed indices,
   not accuracy or calibration metrics.
6. Clicking the graph finding opens its source/value in the side panel. Clicking
   the red relationship shows CONTRADICTED, its reference provenance and evidence ID.
7. Unconfigured research is disabled with the explicit TAVILY_API_KEY reason.

## Remaining limitations and compatibility

- Monetary classification is deterministic English-context matching, not complete
  language understanding. It intentionally leaves unresolved relationships, ranges
  and alternatives unpriced. Amount roles and periods require local cues; written
  number words, `45k` abbreviations and arbitrary multilingual syntax are not covered.
- Unpunctuated clauses with more than 64 monetary amounts are left unresolved to bound matching work. Displayed context windows may be shortened; exact amount and label offsets remain available.
- OCR can misread currency glyphs/digits. Preview/correction is required in the UI;
  no OCR accuracy metric is claimed. Native tests cover a clean synthetic English
  image, not every camera/font/layout. No image bounding coordinates are invented.
- Corrected text is recorded as USER_REVIEWED_OCR, with original extraction/file
  hashes, status and correction metadata. Source offsets address that reviewed text,
  not pixels. Signed review tokens expire after 30 minutes or secret rotation;
  an expired token requires extracting the image again.
- The direct screenshot/image endpoint is retained for API compatibility and does
  not force human review. It labels its extraction as unreviewed. OCR failure and
  scanner failure use distinct stage/code error bodies.
- New checklist states extend the API status values. The UI still understands
  historical `passed` values. External API clients should accept `verified`,
  `unavailable` and `not_performed` as well as failed/warning. Archived scan snapshots
  remain immutable; submit a new investigation to replace previously cached amount
  errors. Old stored warnings cannot be retroactively classified as unavailable
  without their original execution metadata.
- Graph relation verification is scoped to recorded comparisons. It does not verify
  recruiter authorization, offer legitimacy, common ownership or criminal activity.
  Large graphs still require zoom/pan. Small screens stack the details panel.
- Live external provider credentials were disabled in validation. Tavily contract,
  provider-failure and budget tests use mocks; no live external verification is claimed.
  LLM remains optional, with deterministic fallback and no scoring authority.
- Inherited scoring is heuristic, the main frontend bundle still triggers Vite's
  size warning, and FastAPI/Starlette emits its existing httpx deprecation warning.
  Distributed execution crash recovery and production deployment hardening remain
  outside these fixes.

## Files modified or added

Source and test files below are relative to the existing project. Documentation
was updated in README.md, API.md, AI.md, BUILD_STATUS.md and this report. Generated
frontend dist assets were rebuilt; no dependency or database migration was needed.

- `backend/app/agents/investigation_orchestrator.py`
- `backend/app/api/v1/endpoints/analyze.py`
- `backend/app/api/v1/endpoints/trust_passport.py`
- `backend/app/ocr/ocr_engine.py`
- `backend/app/scanners/payment_scanner.py`
- `backend/app/schemas/all_schemas.py`
- `backend/app/schemas/investigation.py`
- `backend/app/services/evidence_service.py`
- `backend/app/services/investigation_execution.py`
- `backend/app/services/next_best_investigation.py`
- `backend/app/services/scan_service.py`
- `backend/app/services/screenshot_service.py`
- `backend/app/services/trust_graph_service.py`
- `backend/app/services/verification_service.py`
- `frontend/src/api/client.ts`
- `frontend/src/components/common/EvidenceCard.tsx`
- `frontend/src/components/common/InvestigationPanel.tsx`
- `frontend/src/components/common/ScreenshotReview.tsx`
- `frontend/src/components/common/TrustGraph.tsx`
- `frontend/src/components/common/VerificationChecklist.tsx`
- `frontend/src/components/common/trustGraphLayout.ts`
- `frontend/src/components/common/verificationSummary.ts`
- `frontend/src/pages/AnalyzePage.tsx`
- `frontend/src/pages/ScanResultPage.tsx`
- `frontend/tests/investigation-ui.test.ts`
- `tests/test_accuracy_regressions.py`
