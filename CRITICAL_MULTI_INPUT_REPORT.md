# Critical organization accuracy and multi-input fixes

Updated locally on 1 November 2026 in `/Users/akshaynaik/Desktop/p1test 2/`. Existing React/Vite, FastAPI, database, routes, theme and previous working-tree changes were retained. No application rebuild, dependency/model installation, migration, commit or push was performed. Tag `hackathon-working-v1` remains at `b738fe0a00ba121defcf8693af7081f0811f1965`.

## Corizo before and after

The supplied excerpts reproduced the bug in the baseline. The full original message was not attached as a complete source document, so the regression fixture is explicitly labelled a synthetic reconstruction using the supplied excerpts and expected wording. Extra facts such as duration or certificate association are extracted only when actually present in the submitted text. A separate test verifies they remain absent when those passages are omitted.

| Field / behavior | Baseline reproduction | Updated reproduction |
|---|---|---|
| Primary organization | Microsoft Corporation | **Corizo** |
| Submitted domain | corizo.in | corizo.in; ownership/authorization unresolved |
| Microsoft role | Incorrectly selected as primary | Claimed collaborator, not primary |
| Other collaborators | Not separately modelled | IBM, Deloitte, Wipro, Cognizant, Barclays, Infosys, Genpact, Oracle retained as claimed collaborators |
| Program | Internship only | Training + Internship when stated |
| Duration | Missing | 2–3 months when stated; retained as a range |
| Training fee | Critical unpriced payment finding | Moderate disclosed fee; amount unspecified, authorization unresolved |
| Certificate wording | Not structured | Claimed association “Wipro Dice ID”; not proof that Wipro issues it |
| Placement promise | Not structured | “Placement Assistance (100% Guarantee)” retained as assistance wording; guaranteed job placement not established |
| Organization/domain mismatch | False Microsoft-versus-Corizo finding | No false mismatch |
| Checklist | 2 failed, 7 unresolved | **0 failed, 9 unresolved**, 0 independently verified |
| Assessment | Elevated concern; heuristic index 80 | **Undetermined**, risk score `null` |
| Partnerships / offer authenticity | Not established | Explicitly unresolved |

These are deterministic outputs on the labelled regression fixture, not a judgment about the real company or an authentication of its partnerships, domain ownership, certificates or program.

## Root causes and fixes

1. **Famous-name selection ignored roles.** The old fallback iterated the bundled organization registry and stopped after finding a name, so Microsoft beat an unknown organizer in “Greetings from …”. New role-aware extraction uses explicit organizer/provider/employer labels and greetings before incidental reference matches, and records collaborator lists separately. The compatibility `organization_mentions` path returns primary names only and deduplicates repeated names. Roles distinguish organizer, claimed employer, training provider, collaborator, explicitly claimed certificate issuer, certificate association, claimed domain owner and payment recipient; recruiter identity remains in the existing recruiter claims. All roles remain CLAIMED. No production rule contains “Corizo”. Tests cover several unknown provider names and direct employers.

2. **Unpriced training labels defaulted to critical.** Payment classification treated a non-application fee keyword as an upfront demand. Training disclosures now remain moderate/unresolved unless supported context shows coercion, an outside/personal-account flow or other strong payment concern. Explicit personal-account instructions in a separate clause are retained as their own finding without inventing or borrowing an amount. Existing registration/security/refund, stipend/salary, GST-total and contractual-liability handling remains. A fee disclosure never becomes proof of authorization or fraud.

3. **Canonical identity was not role aware across consumers.** The scanner, structured claims and existing canonical Investigator context now share the primary-organizer extraction. Collaborators and certificate associations have separate claims/citations. Single-scan PDF export now includes submitted identity/program claims with provenance. Case graphs/reports already use the same stored claims. Chat explicitly separates the organizer from collaborators and explains unresolved fee/refund/partnership/certificate questions. Nearby certificate wording cannot invent an issuer relationship.

4. **Analyze did not expose the existing combined-input workflow.** Cases already had secure batch intake. Analyze now embeds that same `CaseIntake` component, creating one case and submitting all selected sources through the existing batch route. Opportunity name, optional organization, text, URLs, PDFs, up to five screenshots and sender email/domain share one action. Single-format tabs remain. Selected URLs/messages/files can be removed; created-case retry/status links and per-source progress are retained. No competing case engine or schema was added.

5. **Graph fitting and overview density needed hardening.** A fresh desktop baseline did not reproduce the completely empty canvas: measured baseline nodes were visible. The exact original failed frame/browser state was unavailable, so its precise cause is not asserted. The component had style-only dimensions and an initial-fit lifecycle without an explicit measured/resize fit controller. Nodes now have explicit initial dimensions and a measured-node/container ResizeObserver fit path. A real React Flow initial-render regression verifies nodes are emitted visibly. Browser checks confirm nodes remain inside the viewport after resizing.

   A separate reproducible readability problem was measured: the program case rendered 13 overview nodes at about 118px width because details forced a tall fit. The default program overview now retains organizer, program, domain, training fee, partnerships and unresolved verification, grouping remaining records into expandable details. On the recorded 49-record browser case, the overview showed eight nodes at about 206px width. All 49 original records remained accessible through expansion/list inspection, and partnership selection showed all nine exact source citations. The six required concepts are visible; no relationship becomes independently verified merely because it was processed.

6. **Dashboard chart labels misrepresented the data source.** `category_distribution` was a Counter over stored CommunityReport records, not scan detections, normalized values or a fixed bar array. The initial three bars at one came from three labelled synthetic demo report records seeded by the existing community route. The frontend nevertheless called them “Top Scam Taxonomies” and included an unsupported hardcoded 48% incident statistic. The chart is now “Community report categories”, explicitly includes the synthetic-record count and states that reports are not confirmed scams/incidents. The 48% statement was removed. API totals retain their existing fields, with additive count/source metadata (`synthetic_count`, `submitted_count`, `data_scope`). Scan metrics explicitly include case-source/demo scans; they are not asserted to be unique authenticated opportunities.

7. **Failed-check language needed precise scope.** Missing/unavailable checks remain unavailable or unperformed, not failed. Removing the false organizer mismatch and contextual fee failure changes the Corizo checklist to zero failures. The UI defines a failed result as a completed check recording a supported concern/inconsistency, and labels its card “Supported concern found”. Completed content checks, warnings, unavailable checks, unperformed checks and independently corroborated claims remain separate. Historical API status names remain compatible; a content completion or bundled reference never authenticates an offer.

## Validation actually executed

| Check | Baseline | Final |
|---|---|---|
| Backend suite, original BEL PDF regression enabled | 325 passed | **350 passed, 0 failed, 0 skipped**, 13.21 s |
| Frontend tests | 15 passed | **18 passed, 0 failed, 0 skipped** |
| TypeScript / Vite production build | Passed | Passed; 3,095 modules |
| Existing synthetic benchmark | Existing fixed dataset | 45/45 scenarios passed |
| Browser combined intake | — | Analyze → optional text + URL → one existing Cases record; URL removal before submit tested |
| Browser canonical chat | — | Corizo as organizer; collaborators and all fee/authorization unknowns kept separate |
| Browser graph | — | Initial visible nodes, readable overview, all-record expansion, partnership citations and resizing passed |
| Dashboard API/browser | — | Actual stored counts and explicit synthetic-report source labels passed |
| PDF/API history | Existing regression suite | New Corizo single/case report checks and retained saved-scan behavior passed |

Intermediate failures were fixed before completion: the new role parser initially duplicated primary-name claims in three existing benchmark tests; a new test exposed a separate personal-account demand being missed; a display-sorting edit accidentally affected the comparison helper and was caught by frontend tests/TypeScript. Existing assertions were not weakened and no tests/features were removed. Final checks pass. The inherited TestClient deprecation and large-bundle warning remain.

### Required A–O coverage

| Requirement | Executed coverage |
|---|---|
| A Corizo with MNC collaborators | New exact-role, amount-unknown, span, graph, checklist and assessment regression |
| B Direct genuine-looking company internship | New Microsoft/Google direct-employer regressions; authenticity remains unresolved |
| C Training provider with partners | New regressions for SkillBridge Academy, Orbit Learning and Future Path Labs; no registry special case |
| D Stipend and separate training fee | New ₹45,000 compensation / ₹5,000 training / ₹999 registration regression; existing stipend/fee tests retained |
| E PDF GST fees and exemptions | Existing original BEL PDF and contextual policy/tax tests passed |
| F Screenshot only | Existing single-screenshot and native OCR/review tests passed |
| G Text + URL | Existing combinations plus new browser Analyze-to-case flow passed |
| H PDF + text + five screenshots | Added API combination passed |
| I URL + PDF + text + five screenshots | Added API combination passed |
| J Unavailable URL with other sources processed | Added all-file/five-image partial-failure case passed |
| K Six screenshots rejected | Existing batch and old upload-route limit tests passed |
| L Duplicate screenshots / confidence | Existing duplicate confidence/coverage tests plus five-image duplicate grouping passed |
| M Initial non-empty graph | Actual React Flow component SSR test plus loaded-browser visibility/bounds checks passed |
| N Investigator primary matches result | New scan/case chat tests and browser Corizo answer passed |
| O Existing routes/reports | Full existing backend suite passed; no route/schema removals |

The mixed image combination tests use controlled OCR output and real upload/PDF/review services. Native Tesseract also ran in the retained standalone image regression. This is not a claim that every combination was separately uploaded through a browser picker or tested across every OCR/layout/language.

The final browser test used a disposable SQLite database and ports 8015/5180 with no LLM or external provider keys. One two-source case retained URL structure analysis with page extraction explicitly unavailable. The actual case PDF export succeeded, retained Corizo/training claims and unresolved verification, and contained no false Microsoft/domain mismatch. The recorded graph case remained inspectable after a 900px responsive resize: eight nodes had nonzero visible bounds, all intersected their canvas; the temporary viewport override was reset.

### Benchmark interpretation

The unchanged 45-scenario synthetic development benchmark passed all cases. Concern detection: TP 16, FP 0, FN 0, TN 29; precision/recall 100%, false-positive rate 0%, abstention 29/45 = 64.44%. Focused annotated extraction: TP 46, FP 0, FN 0, precision/recall 100% within the declared annotation scope.

These are regression figures, **not real-world accuracy**, a held-out evaluation or calibrated probabilities. The added organizer/partner fields are covered by dedicated assertions, not exhaustively measured by the old extraction annotation scope. Labels and rules were developed together; missing or repeated evidence never becomes proof of safety or independent verification.

## Feature-preservation checklist

| Existing feature | Evidence / boundary |
|---|---|
| Text, URL, PDF and screenshot single-source analysis | Full API/scanner suite passed, including original BEL PDF and native image review; no case required |
| Cases workspace, batch sources, revisions, removal, partial success | Existing/new integration tests passed; Analyze now reuses the same architecture |
| Authentication / ownership / admin controls | Existing private-case/scan/report and new-case-route authorization tests passed; no middleware/security toggle removed |
| Dashboard | Aggregation API tests and updated browser labels passed; existing cards/charts remain |
| History / saved scans / comparison | Existing persistence and integrity tests passed; historical snapshots not silently rewritten |
| Community | Existing create/list flow and new aggregation-count test passed; chart represents reports, not confirmed incidents |
| AI Investigator | Existing deterministic fallback plus role-grounded scan/case tests passed; no model/API required |
| TrustGraph | Existing layout/provenance tests, actual component render, compact/detail expansion and browser visibility passed |
| Next Best Investigation / exact notice | Existing execution, idempotence, provenance, retrieval-boundary and unavailable-provider tests passed |
| Trust Passport / saved reports / scan PDFs | Existing API suite passed; canonical submitted identity now included in scan PDF output |
| Unified case report | New Corizo API export check passed; no new provider call on export |
| Emergency recovery | Existing guidance API regressions passed; no real-world recovery action performed |
| Browser extension | Source/routes left unchanged; installed extension/background/content-script runtime not tested |
| Theme/navigation/page structure | Existing design retained; targeted Analyze/Cases/Dashboard browser checks passed; every historical UI page was not manually visited |
| SSRF, upload validation, redaction, rate limits | Full existing security regressions passed; no security protection disabled |

No database migration, new endpoint, dependency, LLM or second investigation system was needed in this update. Existing responses receive additive claim/metric metadata. No automatic Git commit or push was made; no real API key was added or staged.

## Manual multi-source walkthrough

1. Restart the existing backend/frontend so the current code loads. Open `/analyze` and click **Add multiple sources**. The original single-format tabs remain below.
2. Enter an opportunity name. Paste only text to test the minimal path, or add optional URLs, PDFs, up to five screenshots and a sender email/domain. Optional organization input is a submitted claim.
3. Inspect the selected evidence preview. Remove a URL/message/file if needed. Click **Analyze All Evidence** once; the existing Cases record is created and all selected sources are submitted together.
4. Review/correct extracted PDF/image text before clicking **Investigate reviewed text** on each file. Extraction is not independent verification. Unavailable/failed sources retain their reasons; successful sources continue.
5. Inspect organizer, collaborator, certificate, stipend/fee and promise scopes under What we found. Review unresolved questions and exact citations. Expand the graph/detail group or select a relationship; original records remain available.
6. Ask the Investigator “Is this company genuine?” or “Are these partnerships and certificates genuine?” The primary organizer should match the result; no submitted affiliation should be called authenticated without independent evidence.
7. Add more evidence to the same case, inspect previous revisions and download the unified PDF. Try a sixth screenshot to confirm rejection, or omit URLs/PDFs entirely to confirm optional types are skipped.
8. On Dashboard, read “Community report categories” as stored report counts including the explicitly indicated synthetic records; do not interpret the bars as confirmed incidents or scan taxonomy frequencies.

For the supplied Corizo excerpts, primary extraction is now Corizo, not Microsoft. A complete original message with different wording can still expose untested patterns; do not infer missing duration/certificate/fee facts just to match this fixture.

### Run / validate on this Mac

```sh
cd "/Users/akshaynaik/Desktop/p1test 2/backend"
source "/Users/akshaynaik/Documents/Codex/2026-11-01/do-not-make-gemma-or-any/work/venv/bin/activate"
AI_PROVIDER=none uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```sh
cd "/Users/akshaynaik/Desktop/p1test 2/frontend"
npm run dev
```

Keep the same database/working directory and existing `.env` as before. No new migration is necessary. Old saved scans preserve their old findings; **resubmit or reprocess** them to obtain the new role-aware result.

From the project root with the Python environment active:

```sh
BEL_REGRESSION_PDF='/Users/akshaynaik/Downloads/Vacancy for  BE  In BEL.pdf' python -m pytest tests -q -p no:cacheprovider
cd frontend
node --experimental-strip-types --test tests/*.test.ts
npm run build
```

## Remaining limitations

- Extraction remains conservative English-pattern matching, not universal relationship understanding. Novel prose, unlabelled organizers, unusual lists, multilingual/OCR-damaged text or complex ownership conditions may remain missing/ambiguous. A website resemblance is not used to invent its owner.
- The full original Corizo message was not supplied as a complete source file; regression inputs are labelled reconstructions of the provided wording. No live company, partnership, certificate, recruiter, fee or domain-ownership verification was established.
- The originally reported completely blank graph frame could not be reproduced in the baseline desktop run. Initial-node sizing and measured/resize fitting are now guarded and tested, but the exact historical browser/hidden-container cause remains unconfirmed. Very small screens or expanded large graphs can still require pan/zoom and the accessible record lists.
- Real external-provider credentials, installed extension behavior, all historical browser pages, PostgreSQL/Docker and production deployment were not tested. Existing safe retrieval remains opt-in and bounded; unavailable providers remain unresolved.
- Bulk processing remains request-time and sequential; worker crash recovery/whole-batch retry, parser isolation, retention/erasure policy and large report layout limits remain as documented previously.
- The dashboard counts stored scans and shared report records, including explicitly labelled demos. It does not measure unique opportunities, scam prevalence or confirmed incidents. The old unsupported 48% statement was removed rather than replaced with invented statistics.
- Ordinary training fees remain unresolved, not authorized. Explicit personal-account/coercive requests still warn. Neither absence of concerns nor processing completion establishes authenticity.

## Files modified or added in this update

- `API.md`
- `ARCHITECTURE.md`
- `BUILD_STATUS.md`
- `CRITICAL_MULTI_INPUT_REPORT.md`
- `README.md`
- `backend/app/agents/investigation_orchestrator.py`
- `backend/app/api/v1/endpoints/dashboard.py`
- `backend/app/scanners/org_scanner.py`
- `backend/app/scanners/organization_roles.py`
- `backend/app/scanners/payment_context.py`
- `backend/app/services/ai_investigator.py`
- `backend/app/services/case_assessment.py`
- `backend/app/services/case_claims.py`
- `backend/app/services/cross_source_service.py`
- `backend/app/services/investigator_context.py`
- `backend/app/services/program_claims.py`
- `backend/app/services/program_graph.py`
- `backend/app/services/report_generator.py`
- `backend/app/services/scan_service.py`
- `frontend/src/components/cases/CaseIntake.tsx`
- `frontend/src/components/common/TrustGraph.tsx`
- `frontend/src/components/common/VerificationChecklist.tsx`
- `frontend/src/components/common/graphOverview.ts`
- `frontend/src/components/common/recruitmentPresentation.ts`
- `frontend/src/components/common/trustGraphLayout.ts`
- `frontend/src/pages/AnalyzePage.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/tests/graph-render.test.ts`
- `frontend/tests/recruitment-review.test.ts`
- `frontend/tests/reliable-workspace.test.ts`
- `tests/fixtures/corizo_role_synthetic.txt`
- `tests/test_organization_roles.py`
