# API

Base path: `/api`. Full runtime schemas: `/docs` and `/openapi.json`.

Existing analyze, scan, auth, emergency, community, dashboard, comparison, passport
and report routes remain. Scan responses retain field names and include `investigation` and an explicit
`assessment`. Primary `risk_level` is ELEVATED CONCERN or UNDETERMINED; `trust_score`
is nullable and abstains when undetermined. For concern, the deprecated trust field
is the inverse concern index; `analysis_confidence` is a heuristic fusion reliability
index. Legacy raw values remain in the stored baseline. Use `assessment` for current
semantics; risk and authenticity verification are separate.

## Analyze

`POST /analyze/text`, `/url`, `/email`, `/phone`, `/organization`:

```json
{"input_type":"text","content":"Microsoft internship: pay ₹999 registration fee","target_identifier":"Microsoft"}
```

Input is bounded to 50,000 characters. Image/PDF endpoints accept validated uploads
up to 10 MB. Unreadable OCR returns 422; no synthetic text is substituted. Arbitrary
metadata submitted to `POST /scans` cannot create trusted document findings.

`GET /scans/{id}` returns the stored result, including evidence and investigation.
History reads never trigger research or LLM calls. Unknown IDs return 404. Explicit
known demo IDs may be materialized as synthetic cases only in demo mode.

## Investigation

- `GET /investigations/{scan_id}` — complete persisted investigation.
- `GET /investigations/{scan_id}/evidence` — evidence chain.
- `GET /investigations/{scan_id}/research` — availability, queries and sources.
- `GET /investigations/{scan_id}/graph` — nodes, edges and provenance disclaimer.
- `GET /investigations/{scan_id}/fusion` — calculations, grouped updates, unknowns.
- `GET /investigations/{scan_id}/recommendations` — ranked next steps.
- `GET /investigations/{scan_id}/history` — action execution records.
- `POST /investigations/{scan_id}/actions/{action_id}`:

```json
{"expected_revision":1}
```

Allowed actions: `verify_sender_domain`, `research_warnings`, when recommended and
AVAILABLE. Returns the updated investigation including revision, history and
`last_change` (before/after fusion and reason). Stale/running/unavailable actions
return 409. Manual or unknown actions return 400. Completed actions are idempotent
when sent with the current revision. Search attempts are capped at three total;
the present rule set normally uses at most one initial and one follow-up query.

## Interpretation and research states

`language.provider=deterministic`, `mode=FALLBACK` when no LLM runs. Future LLM
output is `LLM_INTERPRETATION` and unverified. `/ai/investigate` retains deterministic
question answering with explicit mode and evidence IDs.

Research states: COMPLETED, SEARCH_UNAVAILABLE, SEARCH_NOT_PERFORMED. A COMPLETED
query can have zero sources; it does not mean an offer is verified. Source types
are OFFICIAL_DOMAIN (bundled domain reference match) or INDEPENDENT_SOURCE (other
host). Search excerpts stay NOT_INDEPENDENTLY_VERIFIED; claim support/contradiction
is never fabricated from keyword mentions.

## Reports and access

`POST /reports/{scan_id}/save` stores a full evidence/fusion snapshot.
`GET /reports/{id-or-token}` retrieves a saved snapshot. `GET /reports/{scan_id}/pdf`
exports the current stored investigation without rescanning. Saved report tokens
are identifiers, not authorization bypasses. Trust Passports summarize legacy
scores; they are not cryptographic certificates of authenticity.

Local development with DEMO_MODE=true is an explicitly shared demo workspace.
Otherwise use `Authorization: Bearer <token>` from `/auth/register` or `/auth/login`.
Scan and report access requires ownership or ADMIN; unauthorized IDs return 404.
Admin routes require ADMIN. POSTs are limited to 60/minute/IP per process (429).


## Accuracy/usability update: screenshot review and check statuses

`POST /analyze/screenshot/extract` accepts a validated image and returns actual OCR
text, SUCCESS/EMPTY/UNAVAILABLE status, reason/error_code and a signed `review_token`.
It performs no forensic investigation. Review or correct `extracted_text`, then POST
`/analyze/screenshot/reviewed` with `{content, review_token}`. The token expires after
30 minutes. The reviewed content is scanned; the filename is metadata only. Existing
`/analyze/screenshot` and `/analyze/image` remain direct unreviewed compatibility APIs.
Errors identify `stage=ocr`, `ocr_review`, `upload` or `forensics` and a specific code.

New checklist statuses: verified, failed, warning, unavailable, not_performed. Historical
passed is still understood. Unavailable and unperformed checks are unresolved, not
failures. Evidence may include `source_spans` (start/end/text/kind); monetary entities
are persisted in `investigation.monetary_entities`, with compensation/payment/ambiguous
roles. Offsets reference stored redacted/reviewed input text. Old snapshots are not
silently rewritten; re-submit a previous scan to correct an archived amount finding.

Graph edges add `relationship_status`, scoped to actual recorded observations or
reference comparisons. Source-result relationships do not authenticate offers.
Recommendations add an optional `unavailable_reason`; completed automatic actions
remain idempotent with the current revision and do not duplicate evidence.


## Multi-source cases

Case management and source ingestion are available under `/cases`. Mutations require
`expected_revision`; snapshots include sources, exact cited claims, cross-source
findings, fusion, graph and recommendations. Images/PDFs enter NEEDS_REVIEW before
scanners run. Source removal is soft removal with assessment recomputation.

See MULTI_SOURCE_WORKSPACE.md for the full route table, examples, access behavior,
input limits and source extraction states. Existing analyze/investigation/report
routes are retained. Alembic head is `0002_multi_source_cases`.


## Accuracy integrity and Evidence Challenge

`GET /challenge/scenarios` declares three synthetic inputs and expected findings.
`POST /challenge/run/{scenario_id}` runs an allowlisted example through the real
persisted case pipeline and returns actual claims, citations, assessment and pass/fail.
No analysis result is prefilled. Authentication/ownership rules are unchanged.

Single-source state now includes exact `claims` and `source_id`. Findings add
provenance fields and retain original excerpts/spans when captured. `completed`
checks mean a rule ran, not independent verification. Historical passed/verified
content checks project to completed without changing stored snapshots.

`assessment.state` is ELEVATED_CONCERN or UNDETERMINED; `verification_status` remains
UNRESOLVED unless a scoped independent record links to an existing claim. The
positive contract is INDEPENDENTLY_VERIFIED_CLAIM; content/reference/search-snippet
adapters do not create it, and offer authenticity is never promoted by that contract.
See ACCURACY_INTEGRITY_REPORT.md for full compatibility details and evaluation.


## Context-aware recruitment claims and exact-notice action

Single-scan `investigation` and case assessments add recruitment claims and a
`notice_review` containing per-claim comparison status, citations, unknowns and retained
independent document records. Claim values remain submitted claims; claim results may
be UNRESOLVED, POSSIBLE_INCONSISTENCY, CONTRADICTED or INDEPENDENTLY_CORROBORATED.
Offer authenticity remains UNRESOLVED even after scoped corroboration.

Existing action routes now support action ID `verify_notice` under the same revision,
idempotence, ownership and research budget rules. It requires one organization,
advertisement number and title, a bundled trusted website reference, configured Tavily
and enabled bounded public retrieval. Unavailable prerequisites return a reason.
At most two eligible full HTTPS documents are attempted. Search snippets alone cannot
verify claims. Full official-host documents must uniquely match the exact notice.

Evidence adds `fact_key`, `occurrences`, `payment_context`, `source_ids` and `citations`.
`source_spans` can include one-based `page`; all offsets reference retained reviewed/
redacted text. Monetary entities add purpose/role, nearby supporting text, rationale,
recipient/channel (when explicit) and stated base/GST-total relationships. Repetition
is grouped while source references remain available. No new migration is required.
See CONTEXT_AWARE_VERIFICATION_REPORT.md for validation and comparison limits.


## Reliable Cases extension

Existing routes remain. Additive owned routes: multipart POST
`/cases/{id}/sources/batch` with `payload={expected_revision,sources:[]}` plus optional
repeated `files`; POST `/cases/{id}/investigate` with `{question}`; GET
`/cases/{id}/report/pdf`. Batch intake requires at least one source, skips absent
source types and retains per-source failures. Files await text review. Active images
are limited to five through both old and new intake routes. URL/PDF limits default
to ten each (`CASE_MAX_URLS`, `CASE_MAX_PDFS`); total sources remain capped at 25.

Chat uses the canonical stored snapshot and adds citations/context_revision. Fee
claims add structured fee_policy_rule records; source_limits and manual comparison
metadata are additive. OFFICIAL_NOTICE_FETCH_ENABLED is a separate default-off
trusted-host retrieval switch; arbitrary CASE_URL_FETCH_ENABLED is not enabled by it.
No migration or breaking route change was added. See RELIABLE_WORKSPACE_REPORT.md.


## Organization-role accuracy and dashboard scope

Existing routes/keys remain. Structured claims add `organization_role`,
`claimed_collaborator`, `duration_range`, `certificate_association`, `placement_promise`
and `fee_policy_disclosure`. Organization claims represent the primary organizer/
employer, not incidental partner names. Each new claim retains source ID, exact
excerpt, location, method and CLAIMED status. Unpriced training disclosures never
invent an amount or authorization.

Dashboard adds `data_scope` and per-category `synthetic_count`/`submitted_count`.
`category_distribution.count` still counts stored community report records, including
labelled synthetic demos; it does not count confirmed incidents or scan detections.
Analyze's combined form uses existing case creation/batch/review/report endpoints;
no new case system, endpoint or migration was added in this phase.
