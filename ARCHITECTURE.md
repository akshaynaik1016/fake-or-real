# Architecture

Existing React/TypeScript/Vite application and FastAPI/SQLAlchemy services are
preserved. No second application or parallel scan engine was created.

```text
Submitted text / URL / email / phone / OCR / PDF
  → size/type checks + credential redaction + URL destination boundaries
  → existing deterministic forensic scanners
  → existing weighted Trust Score (legacy baseline)
  → InvestigationOrchestrator
      ├─ normalized evidence + submitted entities
      ├─ Tavily (optional, fixed endpoint, bounded calls)
      ├─ LanguageProvider (optional, interpretation only)
      ├─ Evidence Fusion (HEURISTIC unless calibrated ratios supplied)
      ├─ NetworkX TrustGraph → React Flow
      └─ rule-ranked Next Best Investigation
  → atomic scan + investigation snapshot persistence
  → existing results page / investigator / comparison / passport / PDF / history
```

## Persistence and replay

Legacy `scans`, `scan_evidence`, `verification_results`, users and report tables
remain intact. Additive `investigation_states` holds a versioned JSON aggregate
containing evidence, sources, relationships, recommendations, calculations, check
coverage, language mode, baseline output and execution history. This avoids six
unnecessary duplicate entity tables. `investigation_executions` records each completed
follow-up and before/after explanation. Alembic revision `0001_investigations` adds
only these tables and can run after existing `create_all` startup.

A scan and snapshot are persisted in one transaction. Reads use stored data; they do
not rerun live scanners, research or a model. Historical scans are conservatively
backfilled from retained evidence with UNKNOWN provenance/coverage. They are not
silently reverified. Existing IDs and legacy history remain readable.

## Follow-up execution

Only allowlisted recommended automatic actions can execute: bundled sender-domain
comparison and a bounded research query. Manual instructions cannot be executed
as tools. Clients send `expected_revision`; an atomic compare-and-update reserves
the next revision before network calls. Concurrent/stale requests return 409,
completed actions are idempotent, and research attempts consume the budget even on
provider failure. History, graph, fusion and report snapshot are refreshed together.
An already-known correlated observation may leave the risk score unchanged, which
is reported explicitly. A worker crash after reservation leaves a RUNNING record;
a durable queue/lease recovery is not implemented (see LIMITATIONS.md).

## Existing functionality

Scanners, emergency guidance, authentication, dashboard, community reports,
comparison, PDF export, Trust Passport and browser-extension source remain.
Dashboard metrics now come from records. Demo reports are labelled synthetic.
VirusTotal/URLhaus adapter placeholders report UNAVAILABLE rather than fabricated
CLEAN results. Browser extension remains an inherited component, not a new security
boundary. Native OCR requires Tesseract; PDF extraction uses pypdf.


## Multi-source case layer

`case_service` composes the existing scan persistence and investigation engine. New
case/source/claim/comparison/revision tables are additive (`0002_multi_source_cases`).
Sources pass existing validators and extraction; images/PDFs await reviewed text.
`case_claims` records exact stored-text offsets; `cross_source_service` produces cited
claim comparisons. `case_assessment` groups identical content, reuses `fuse_evidence`
and constructs the case graph and next checks. Single-source routes remain unchanged.

Every mutation creates a complete immutable snapshot using an expected-revision
compare/update. Removed sources are excluded from current calculations but retained
for audit. Automatic case actions reserve a running state, call the allowlisted
existing executor or bounded Tavily adapter, then recompute. No LLM enters the case
scoring path. Optional public URL text retrieval uses validated pinned IPs, HTTPS
SNI/certificate verification, redirect validation and bounded passive content.

The UI adds `/cases` and `/cases/:id` to the existing router and React Flow graph.
MULTI_SOURCE_WORKSPACE.md documents request-time processing, retention, duplicate
detection and other operational limits.
