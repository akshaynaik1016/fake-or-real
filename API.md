# API

Base path: `/api`. Full runtime schemas: `/docs` and `/openapi.json`.

Existing analyze, scan, auth, emergency, community, dashboard, comparison, passport
and report routes remain. Scan responses retain their original fields and add
`investigation`. Existing weighted trust/risk/confidence fields remain legacy
baseline values; the new `investigation.fusion` contains the current assessment.

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
