# Multi-source investigation workspace — implementation and validation

Updated in place: `/Users/akshaynaik/Desktop/p1test 2`.
Date: 1 November 2026. No application rebuild, new model, LLM dependency or new package installation. Existing single-source scans and the optional provider-independent language interface remain available. Case reasoning and scoring are deterministic.

## Implemented behavior

- `/cases` creates and lists named cases; `/cases/:id` manages one opportunity across image, PDF, URL, text, email and phone sources. Source processing, extraction failures, review state and removal are visible. Images/PDFs require the user to review or correct extracted text before investigation.
- Five additive tables persist cases, sources, structured claims, cross-source findings and immutable assessment revisions. Every mutation checks the expected revision. Non-demo access enforces case ownership.
- Existing validators, OCR/PDF extraction, monetary entities, forensic scanners, source investigation persistence and Evidence Fusion are reused. Source cards link to their preserved single-source investigation.
- Claims cover organization, opportunity type, role, compensation, payment, duration, recruiter, email, application URL/channel, phone and sensitive requests. Each records an exact excerpt, source ID, extraction method, CLAIMED status and character offsets into stored extracted/reviewed text. PDF page metadata is retained when available. Filenames are display metadata only.
- Comparisons distinguish confirmed contradictions in stated claims, possible inconsistencies, supporting claims and new information. Missing fields appear separately as unresolved information. Conflicting compensation requires matching currency, compensation category and period. Decimal formatting differences are normalized. An absent fee field is not a contradiction; an explicit no-fee instruction can contradict a payment request.
- Repeated normalized text is grouped as duplicate content. Copies do not add independent fusion confidence or coverage. Removing the original promotes the remaining copy. Source removal/correction recomputes active claims, comparisons, graph and assessment; earlier snapshots retain their original state.
- Case fusion separates risk, confidence and coverage, preserves existing correlation groups, cites additional claim-disagreement signals and labels the result HEURISTIC. A reassuring poster or organization reference match alone remains UNDETERMINED. Submitted disagreements are not proof of fraud.
- Existing React Flow graph adds cases, source documents, extracted entities and cited comparisons. Relationships distinguish observed, claimed, independently verified, contradicted and unresolved states. Full evidence and source links appear in the side panel and accessible entity list.
- Next Best Investigation executes the existing sender-domain comparison or bounded optional Tavily search. Completed checks persist real results and refresh the case. Manual tasks stay unperformed. Running/stale requests are rejected; completed sender checks do not duplicate evidence. Search snippets never authenticate an offer or enter risk as verified facts.
- URL page retrieval is optional (`CASE_URL_FETCH_ENABLED=false` by default). Without it, URL structure is scanned and page extraction is explicitly unavailable. Optional retrieval rejects internal/private addresses, pins validated IPs, preserves HTTPS hostname/certificate verification, revalidates every redirect, and bounds time, response size, redirects and content types. No document text is sent to search; search uses organization context.

## Design causes addressed

The previous persistence and routes represented one submission per scan, so there was no aggregate case, source lifecycle or revision-aware cross-source state. The new case layer composes existing scans instead of replacing them. Previously, matching claims had no cross-document provenance contract; cited structured claims now make each comparison reviewable. Reassuring source-level reference matches cannot establish opportunity authenticity, so the case-level sufficiency guard keeps such cases undetermined. Exact duplicates are grouped before case fusion to prevent repeated submissions from becoming independent support.

The earlier payment, screenshot review, five-state checklist and single-source TrustGraph fixes are preserved. Their root causes and original verification remain documented in `ACCURACY_USABILITY_REPORT.md`.

## Validation actually executed

| Check | Result |
|---|---|
| Pre-change backend baseline | 145 passed, 0 failed |
| Full final backend suite | **187 passed, 0 failed, 0 skipped**, 4.93 s |
| Frontend logic tests | **5 passed, 0 failed** |
| TypeScript + Vite production build | Passed; 3,088 modules |
| Migration upgrade and repeat upgrade | Passed on disposable copy reconstructed to pre-case schema; all 17 existing tables retained with identical row hashes/counts, including 28 scans; five case tables added; head `0002_multi_source_cases` |
| Browser smoke with isolated SQLite/API and no LLM/API keys | Case creation, two text/email sources, cited stipend/channel conflicts, ₹999 payment evidence, real sender check, updated fusion/graph, historical read-only view and source removal/recomputation passed |

Scenario A: image poster extraction/review yields organization/opportunity and UNDETERMINED. B: second-source ₹999 fee updates the same case. C: generated PDF + message stipend disagreement cites both sources. D: duplicate image contents do not increase confidence. E: removal clears dependent findings while history remains. F: mocked OCR failure stores an explicit failure with no fabricated claims/findings. G: unavailable search remains unresolved. All A–G pass API integration tests. OCR success/failure is controlled in the image case tests; these are not seven browser upload tests. The full suite also retains the previously added real native Tesseract regression.

Additional tests cover exact spans, missing fields, organization/domain/channel/duration differences, amount precision and period ambiguity, duplicate promotion, corrections, ownership, stale revisions, running-check protection, removal during a running check, action idempotence, search success/failure budgets, original URL scanner input, public redirect validation, private targets, pinned IPs, SNI/certificate hostname, size/type/encoding limits, DNS failure and timeout.

Commands (from the project root with the project Python environment activated):

```sh
python -m pytest tests -q -p no:cacheprovider
cd frontend
node --experimental-strip-types --test tests/*.test.ts
npm run build
```

Verification environment: macOS arm64, Python 3.15.0, Node 26.3.1, npm 11.16.0, Vite 8.3.5. One existing upstream FastAPI/Starlette TestClient deprecation warning remains. Vite reports the inherited main bundle above 500 kB. No live Tavily, live public page retrieval, production/PostgreSQL, Docker or small-screen browser certification is claimed.

## Run the updated application

Use the existing Python environment and frontend dependencies. Do not overwrite an existing `.env`. With no model configured, retain `AI_PROVIDER=none`.

```sh
cd "/Users/akshaynaik/Desktop/p1test 2/backend"
# Activate your existing Python environment first.
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```sh
cd "/Users/akshaynaik/Desktop/p1test 2/frontend"
npm run dev
```

Open `http://localhost:5173/cases`. Create a case and add evidence. Approve/correct image/PDF text in its source card before investigation. Use Assessment history for read-only snapshots. Existing `/analyze`, `/scan/:id`, history and reports remain.

Use the same `DATABASE_URL` and backend working directory as before; an absolute SQLite path avoids selecting the other inherited database. Run the additive migration against your selected database before starting/restarting. The migration was tested on a copy; no deliberate migration command targeted the user's working database. The inherited startup `create_all` can also create missing additive tables, but does not replace Alembic version tracking. The temporary browser test used a separate database and ports 8011/5176.

Optional `TAVILY_API_KEY` enables organization-context search. Optional `CASE_URL_FETCH_ENABLED=true` enables bounded public page text retrieval. Native Tesseract is needed for images. Missing dependencies/services produce explicit unresolved or extraction states. No Gemma setup is needed.

## API additions

All paths below are prefixed `/api`; existing auth/demo access rules apply.

| Method | Path | Input |
|---|---|---|
| GET / POST | `/cases` | POST `{title}` |
| GET / PATCH | `/cases/{id}` | PATCH `{title, expected_revision}` |
| POST | `/cases/{id}/sources` | `{input_type: text|url|email|phone, content, title?, expected_revision}` |
| POST | `/cases/{id}/sources/upload` | Multipart `file`, `input_type=screenshot|pdf`, `expected_revision`, optional `title` |
| POST | `/cases/{id}/sources/{source_id}/review` | `{content, expected_revision}` |
| DELETE | `/cases/{id}/sources/{source_id}` | JSON `{expected_revision}` |
| GET | `/cases/{id}/revisions` | Latest 200 revision summaries |
| GET | `/cases/{id}/revisions/{revision}` | Immutable full snapshot |
| POST | `/cases/{id}/actions/{action_id}` | `{expected_revision}`; use returned recommendation ID |

Stale mutations return 409; foreign case/source IDs return 404. Do not construct arbitrary action IDs. Responses include source states, claims, comparisons, fusion, graph, recommendations and revision metadata. Maximum 25 active sources per case; text 50,000 characters and existing upload size/type limits apply.

## Files added

```
backend/app/schemas/cases.py
backend/app/services/case_claims.py
backend/app/services/cross_source_service.py
backend/app/services/case_url_fetcher.py
backend/app/services/case_assessment.py
backend/app/services/case_service.py
backend/app/api/v1/endpoints/cases.py
backend/migrations/versions/0002_multi_source_cases.py
frontend/src/api/cases.ts
frontend/src/pages/CasesPage.tsx
frontend/src/pages/CaseWorkspacePage.tsx
frontend/src/components/cases/CaseSourceCard.tsx
frontend/tests/case-layout.test.ts
tests/test_multi_source_cases.py
MULTI_SOURCE_WORKSPACE.md
```

## Files modified

```
backend/app/models/all_models.py
backend/app/api/v1/api.py
backend/app/core/config.py
backend/app/services/scan_service.py
backend/app/api/v1/endpoints/analyze.py
frontend/src/App.tsx
frontend/src/api/client.ts
frontend/src/components/common/TrustGraph.tsx
frontend/src/components/common/trustGraphLayout.ts
frontend/src/components/layout/Navbar.tsx
tests/conftest.py
tests/test_investigation.py
README.md
API.md
ARCHITECTURE.md
BUILD_STATUS.md
```

The existing migration test's expected head was updated to `0002_multi_source_cases`; its data-preservation assertions remain. Existing tests/features were retained. Frontend build artifacts were regenerated by the build. The actual `.env` was neither copied nor edited; no credential is included in this report.

## Known limitations

1. Claim extraction uses conservative patterns and bundled organization references, not general semantic understanding. Unlabelled roles/recruiters and complex wording may remain missing. Comparable compensation/duration rules avoid some false contradictions but cannot resolve differing roles, dates, eligibility tiers or offer versions automatically; users must interpret the cited disagreements.
2. Duplicate detection uses normalized text equality, not visual/perceptual or semantic similarity. Related paraphrases and modified copies may remain separate; correlation groups still limit repeated scanner categories.
3. Confidence and coverage are heuristic. No calibrated fraud probability or proof of offer authenticity is supplied. Independent human verification remains necessary.
4. Image/PDF text requires review; scanned PDFs without readable text fail explicitly and need manual transcription/image OCR. Locations reference extracted/reviewed text, with page metadata where available, not image bounding boxes or an original-file forensic archive. Raw uploaded files are not retained by this case feature.
5. Source removal is an audit-preserving soft removal. Historical snapshots and preserved scans retain source text; this is not a privacy-erasure operation. A retention/deletion policy and restore UI are not implemented.
6. Processing uses request-time work, not a durable background queue. A worker crash may leave a source PROCESSING or a check running; automatic lease recovery/retry is not implemented. Case updates use revision checks, but high-load/distributed behavior and PostgreSQL have not been exercised.
7. URL retrieval defaults off, supports passive public HTML/plain text only, rejects compressed responses and does not run JavaScript or authenticate to sites. Live network retrieval and live Tavily credentials were not exercised; network contracts/failures were mocked. Search snippets remain unverified context.
8. Only local sender-reference comparison and optional Tavily search execute automatically. Fee authorization, direct organization contact, offer letters and application-route verification remain explicit manual steps. Reference-domain matches do not prove sender authorization.
9. Large graphs can require zoom/pan or the accessible entity list. Responsive classes are present, but browser verification was at desktop width. Case PDF export, source reordering, bulk upload, case deletion and migrating old scans into cases are outside this implementation; existing single-scan report/export remains.
