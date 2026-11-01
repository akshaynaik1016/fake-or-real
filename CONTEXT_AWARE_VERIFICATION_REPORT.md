# Context-aware evidence verification: implementation and validation

Updated 1 November 2026 in the existing `/Users/akshaynaik/Desktop/p1test 2` checkout. FastAPI, React/Vite, React Flow, case architecture, deterministic investigator, Evidence Fusion and Next Best Investigation remain in place. The supplied `p1test 3.zip` code matched this checkout before this update. No model, dependency or database migration was added. No `.env` or original PDF was changed.

## Original PDF: reproduced failure and observed result

The original file was located at `/Users/akshaynaik/Downloads/Vacancy for  BE  In BEL.pdf`. It has 16 pages and SHA-256 `5f4ffad40045db812cac1cddd0c54a0d7e3a36d46a8e7371972277a8e9e2652c`. The original binary is not bundled with the tests. The baseline was replayed from the pre-change scanner/services on this exact file with network providers and LLMs disabled. The updated file was also submitted through the real PDF API to a disposable SQLite database and inspected in the browser.

| Observation | Before | After |
|---|---|---|
| Assessment | Elevated concern; fusion risk index 95/100 | Undetermined; risk score `null` |
| Critical findings | 9 | 0 |
| Evidence | 29 raw scanner findings; 10 investigation findings | 3 distinct investigation findings |
| Repeated application-fee policy | Repeated critical payment warnings | One moderate unresolved fee-policy finding, with all supporting references |
| ₹1,000 + GST = ₹1,180 | Repeated payment amounts | Explicit related base/total amounts; no assumed GST rate |
| ₹2,00,000, page 9 | Included in misleading payment-risk context | Contractual penalty/liability, not an upfront fee |
| Account creation, login and system credential delivery | Critical password warning | Account instructions, not an outward secret request |
| Specific offer authenticity | Unresolved, despite alarming keyword score | Explicitly unresolved throughout |

The three final findings are a neutral bundled company/domain reference observation, one moderate application-fee policy observation and one moderate internal fee-policy inconsistency. The PDF requires GEN/EWS/OBC payment on page 5 and EWS payment in the FAQ on page 15, but includes EWS in exemptions on pages 11 and 13. All four passages are retained. This inconsistency warrants clarification; it does not prove fraud. The neutral domain reference is excluded from the concerns section and is not independent verification of this advertisement.

The document's 28 October 2026 publication date, 350 vacancies, Probationary Engineer title, advertisement number, 18 November 2026 deadline, eligibility, fee/exemption instructions, claimed website and account instructions are extracted with exact text/page provenance. A labelled vacancy-table total is used; the company's unrelated reference to 350 products is not treated as the vacancy count.

The earlier ₹45,000/month stipend versus ₹999 registration-fee fix remains covered by the passing suite and synthetic benchmark. A fee amount is not borrowed from another compensation sentence when association is unclear.

## Root causes and corrections

| Root cause | Correction and relevant path |
|---|---|
| Payment labels and amounts were assessed independently, with insufficient purpose/channel/recipient and document context. Contract liabilities and normal application fees could trigger fee-demand rules. | Extend the existing monetary parser with clause/page context, monetary roles, stated tax relations and rationale. Application fees remain unresolved; explicit personal/outside-flow or coercive demands remain concerning. `payment_context.py`, `payment_scanner.py`, `scan_service.py`. |
| Repeated fee labels, text scanner copies, amounts and copies across sources produced multiple evidence rows and exaggerated contributions. | Group underlying policy facts using rule-based semantic keys and retain occurrences, source IDs and every distinct span. Different purposes, recipients and channels retain separate findings. Existing fusion correlation grouping limits weight. `evidence_service.py`, `cross_source_service.py`, case and scan assessment. |
| Generic secret/document keywords ignored direction and purpose. `enter` prefix matching also matched “Enterprise”; “passport size photograph” resembled a Passport request. | Distinguish account creation/login/system delivery from asking applicants to send secrets to another person. Use explicit verb forms and suppress the photo phrase, without suppressing outward password/OTP requests. `sensitive_data_scanner.py`, `text_scanner.py`. |
| Generic recruitment extraction missed table totals, compact `forRs.1000`, scoped exemptions and advertisement-header dates. | Add deterministic labelled recruitment patterns, original offsets/pages, supported monetary relationships and category-scoped policies. Ambiguous dates/amounts stay ambiguous. `recruitment_claims.py`, `case_claims.py`. |
| Company-domain references and generic search context were insufficient to compare the exact advertisement; the API had no executable exact-notice retrieval action. | Add `verify_notice` through existing action/revision/budget/persistence paths. Search exact organization, advertisement number and job title, retrieve bounded full documents on a trusted HTTPS domain, then compare individual claims with both excerpts. General snippets/uploads cannot establish independent corroboration. `notice_verification.py`, action services, URL fetcher. |
| Result screens exposed a long technical evidence chain, repeated claims and legacy “verified” severity labels. | Add five plain-language sections, grouped claim citations and notice/fee/channel relationships in the existing graph. Advanced evidence remains available. Reference observations are labelled separately, including in PDF export. `RecruitmentReview.tsx`, presentation helpers, graph/result components, report generator. |
| Internal EWS exemption conflict would otherwise disappear when reducing the false-positive payment findings. | Preserve a moderate scoped policy inconsistency citing required-payment and exemption passages. Do not classify this alone as proven fraud or independent contradiction. `recruitment_consistency.py`. |

## Evidence and verification integrity

Monetary records retain exact amount text/currency, category, role, supporting context, classification rationale and source span/page. Roles distinguish compensation, payment demands, contractual liabilities, reimbursements and ambiguous mentions. Categories include application, registration, processing/training/security deposits, salary, stipend, scholarship, refundable payment, contractual penalty, reimbursement and other/ambiguous uses. Unclear relationships are not filled in with a guessed amount or recipient.

A document saying it uses an official gateway creates a submitted claim, not verified ownership or payment authorization. In the original PDF the exact recipient/payment URL is not inferred. No company allowlist exempts a document from explicit harmful requests. Malicious requests embedded alongside normal account instructions still trigger warnings.

`verify_notice` requires unambiguous organization, advertisement number and job title, a bundled trusted website reference, configured Tavily, enabled bounded public retrieval and available research budget. It attempts at most two eligible full-document fetches per action, including failed attempts. HTTPS host boundaries, public-destination restrictions, pinned TLS/redirect guards, timeouts and size limits remain active. PDF retrieval is limited to 2 MiB; ordinary text fetching retains its 512 KiB bound. Truncated or invalid documents cannot corroborate claims.

Independently retrieved records retain URL, retrieval time, content hash, retrieval method, original text and claim citations. Matching full-document exact-notice claims can be independently corroborated in that narrow scope. Unambiguous conflicting dates/vacancies/destinations or clearly comparable fee totals can create independently sourced contradictions with both citations. Uncertain fee tax/category differences remain possible inconsistencies. Uploads, client-provided “verified” metadata, snippets, another notice and duplicate copies do not enter this path as independent evidence. Repetition cannot multiply an independent contradiction's weight. Even corroborating advertisement fields does not authenticate the uploaded file, recruiter or payment transaction.

BEL's domain reference uses the government [India Science and Technology institutional listing](https://www.indiascienceandtechnology.gov.in/allstinstitutions/bharat-electronics-limited-bel). That reference establishes only a company/website comparison. No exact BEL advertisement was independently authenticated in this task. Attempts to inspect BEL's public recruitment site were unavailable; live Tavily retrieval was not exercised. The actual regression and browser run intentionally used no LLM, no provider keys and disabled live external scanners.

Risk and verification stay separate. No suspicious finding and unavailable external checks do not produce safety evidence. Fusion indices are heuristic, not calibrated probabilities. Completed deterministic content checks are not independent verification. The existing provider-independent optional LLM interface remains unchanged; no LLM can set the final score or introduce factual evidence.

## Validation actually executed

| Check | Result |
|---|---|
| Pre-change full backend baseline | 241 passed |
| Final full backend suite, original PDF regression enabled | **297 passed, 0 failed, 0 skipped**, 10.05 seconds |
| Frontend logic tests | **12 passed, 0 failed, 0 skipped** |
| TypeScript and Vite production build | Passed; 3,092 modules |
| Existing synthetic accuracy benchmark | 45/45 scenario checks passed |
| Original PDF through real PDF API and browser | Undetermined, 0 critical, grouped fee and cited EWS inconsistency; expanded amount citations and account/penalty classifications inspected |
| PDF export through real report endpoint | HTTP 200, PDF content type, 2 pages; unresolved authenticity, reference-observation label, grouped fee and EWS conflict present; no critical findings |

There are 56 additional backend cases relative to the 241-test baseline. The requested A–H cases are covered in `tests/test_recruitment_context.py`: repeated application policy; explicitly related tax amounts; contractual liability; normal account instructions; outward secrets/personal payments; unverified known company; empty search; and correlated copies across sources. Additional cases cover distinct recipients, ambiguous fee bases/categories, official full-document retrieval success/failure, hostile domains/redirects, two-attempt limits, no allowlist bypass, injected “verified” metadata, source removal, action persistence/idempotence, case and single-scan graph/fusion updates, invalid PDF extraction and the exact original PDF hash.

The three additional frontend tests check grouped source/page references, distinct destinations/tax presentation and non-overlapping notice layout. The full existing suite also covers native AEXON screenshot OCR/review, stipend/fee separation, checklist semantics, unavailable integrations, provider fallback, case contradictions, Evidence Challenge and previous features. Mock transports are used for independent-retrieval success/failure and contradictions; these tests do not claim a live BEL/Tavily integration succeeded.

One inherited FastAPI/Starlette TestClient deprecation warning and the inherited JavaScript chunk-size warning remain. No failing check remains from the executed final validation.

### Re-run

From the project root with the existing Python environment active:

```sh
BEL_REGRESSION_PDF='/Users/akshaynaik/Downloads/Vacancy for  BE  In BEL.pdf' python -m pytest tests -q -p no:cacheprovider
cd backend
python evaluate_accuracy.py --output /tmp/fake-or-real-benchmark.json
cd ../frontend
node --experimental-strip-types --test tests/*.test.ts
npm run build
```

Without `BEL_REGRESSION_PDF`, the portable synthetic fixture and all other tests still run; the single original-binary regression explicitly skips. The supplied synthetic fixture is labelled synthetic. The original-file test verifies the expected SHA-256 before asserting output.

### Synthetic benchmark metrics and limits

The unchanged 45-scenario development dataset has 16 observable-concern positives and 29 abstention examples. Concern precision 16/16 = 100%; recall 16/16 = 100%; false-positive rate 0/29 = 0%; abstention 29/45 = 64.44%. Focused annotated extraction has 46 true positives, 0 false positives and 0 false negatives, giving 100% precision/recall within that annotation scope.

These are descriptive regression measurements on realistic synthetic examples, **not real-world accuracy**. The same development effort wrote labels and rules; there is no independent held-out corpus, statistical calibration, prevalence adjustment or confidence interval. A negative means abstain, not genuine. Unannotated extraction fields are not scored. OCR-noise benchmark inputs replay transcripts; native image OCR is exercised separately. The new context tests extend regression coverage without relabelling the old benchmark as real-world evaluation.

## Compatibility and operation

All existing routes remain. New result fields are additive: monetary context/relations, grouped evidence `fact_key`, `occurrences`, citations/source IDs and exact span pages, recruitment claims and `notice_review`. Existing single-scan and case action routes accept the new `verify_notice` action through their normal revision/idempotence contracts. Public PDF retrieval is opt-in within that action; ordinary URL ingestion retains its prior behavior. No new schema migration is needed beyond the existing case migration `0002_multi_source_cases`.

Restart the backend and frontend to load the changes. Re-submit old scans or recompute cases; immutable archived snapshots are not silently rewritten. Existing `.env`, included databases and user data were not changed. Browser/API checks used an isolated temporary database and ports; no user's running service was replaced.

## Remaining limitations

- Exact independent verification of this original BEL notice remains unavailable. No assurance about paying, the applicant's recipient, recruiter identity or file authenticity was established.
- Rule-based contextual extraction and deduplication are conservative, not universal semantic understanding. Complex tables, multilingual text, OCR damage, long-distance references, novel phrasing, recipients and category scopes may remain missing or ambiguous.
- Exact-notice retrieval deliberately abstains if organization/advertisement/title anchors are missing or non-unique. Multi-post notices, changed job-title wording, authenticated pages or JavaScript-only sites may need manual comparison.
- Fee differences need comparable tax and applicability. Ambiguous exemptions/amount bases are reported as unresolved/possible inconsistencies rather than asserted independent contradictions. A stated GST equation is a text relationship, not tax validation.
- Trusted website references cover a limited bundled list. Website existence never establishes recruiter authorization. Live external credentials and provider responses were not tested here.
- Deduplication uses purpose, normalized values/relations, destination/channel and correlation keys. Distinct but insufficiently described requests may be difficult to distinguish; all source references remain inspectable.
- Existing upload/text/size limits, synchronous PDF/OCR parsing, worker-crash recovery, production/PostgreSQL deployment and small-screen UX limitations remain. No new production security or calibrated fraud-accuracy claim is made.

## Files added or modified in this update

- `API.md`
- `ARCHITECTURE.md`
- `BUILD_STATUS.md`
- `CONTEXT_AWARE_VERIFICATION_REPORT.md`
- `README.md`
- `backend/app/agents/investigation_orchestrator.py`
- `backend/app/api/v1/endpoints/analyze.py`
- `backend/app/scanners/org_scanner.py`
- `backend/app/scanners/payment_context.py`
- `backend/app/scanners/payment_scanner.py`
- `backend/app/scanners/sensitive_data_scanner.py`
- `backend/app/scanners/text_scanner.py`
- `backend/app/schemas/all_schemas.py`
- `backend/app/schemas/investigation.py`
- `backend/app/services/case_assessment.py`
- `backend/app/services/case_claims.py`
- `backend/app/services/case_service.py`
- `backend/app/services/case_url_fetcher.py`
- `backend/app/services/cross_source_service.py`
- `backend/app/services/evidence_service.py`
- `backend/app/services/investigation_execution.py`
- `backend/app/services/notice_verification.py`
- `backend/app/services/recruitment_claims.py`
- `backend/app/services/recruitment_consistency.py`
- `backend/app/services/recruitment_graph.py`
- `backend/app/services/report_generator.py`
- `backend/app/services/scan_service.py`
- `backend/app/services/verification_service.py`
- `frontend/src/api/cases.ts`
- `frontend/src/api/client.ts`
- `frontend/src/components/common/EvidenceCard.tsx`
- `frontend/src/components/common/InvestigationPanel.tsx`
- `frontend/src/components/common/RecruitmentReview.tsx`
- `frontend/src/components/common/TrustGraph.tsx`
- `frontend/src/components/common/recruitmentPresentation.ts`
- `frontend/src/components/common/trustGraphLayout.ts`
- `frontend/src/pages/CaseWorkspacePage.tsx`
- `frontend/src/pages/ScanResultPage.tsx`
- `frontend/tests/recruitment-review.test.ts`
- `tests/fixtures/bel_context_synthetic.txt`
- `tests/test_recruitment_context.py`
