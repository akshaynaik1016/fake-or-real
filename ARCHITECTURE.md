# Final-readiness extension — 2 November 2026

`assessment_dimensions` derives observed concern, scoped authenticity, processing,
and recorded coverage from the same persisted evidence and claims as the existing
assessment. It does not change fusion formulas or let language providers score cases.
`assessment_semantics` projects these fields for legacy snapshots without mutating or
rescanning them. Cases list/revisions, chat and reports consume the same projection.

`dashboard_investigations` deduplicates active cases against current AND historical
source scan IDs while keeping legacy raw-scan metrics. React `AssessmentDimensions`
shares the labels across scan/case/list/history/dashboard views. `GraphView` guards
the lazy graph chunk, and `TrustGraph` retains React Flow with measured fit and
record-list fallback. Full details and limitations: FINAL_DEMO_READINESS_REPORT.md.

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


## Shared uncertainty and accuracy evaluation

`organization_mentions` separates submitted name extraction from reference matching.
The existing cited case extractor is reused for single-source claims; scanner spans
and source identifiers survive persistence. `assessment_semantics` defines concern
versus abstention separately from independent claim verification. Integrity views
project stored data conservatively without rescanning or rewriting historical rows.
Primary API consumers and React labels share this meaning; legacy raw scoring stays
in baseline data for audit. Content completion and reference observations are never
promoted to independent offer authentication.

`evaluation/runner.py` calls existing persisted case services using labelled synthetic
inputs, checks exact provenance and reports separate extraction and concern-policy
metrics. `evaluate_accuracy.py` runs it offline with an isolated temporary database.
The Evidence Challenge endpoint allows only A/B/C fixtures and returns actual stored
case outputs; no arbitrary tool execution or injected provider result is exposed.
See ACCURACY_INTEGRITY_REPORT.md for boundaries and measured development-set results.


## Context-aware recruitment evidence

The existing monetary scanner delegates contextual enrichment to payment_context.py;
the original matcher and investigation contracts remain in use. Evidence grouping is
shared by scan and case assessment before fusion. recruitment_claims.py extracts
labelled notice metadata, while recruitment_consistency.py preserves scoped internal
fee-policy inconsistencies. Normal account instructions are handled separately from
outward credential requests by the existing sensitive-data scanner.

notice_verification.py adds an exact-notice action through existing execution,
reservation, budget and persistence services. It searches exact anchors, retrieves
bounded full documents on a trusted HTTPS host and compares scoped claims. Independent
records retain retrieval provenance. User uploads and snippets cannot enter as
independent corroboration; an organization reference cannot authenticate an offer.
recruitment_graph.py extends existing graph assembly and React Flow rendering with
notice, fee and channel relationships. RecruitmentReview reuses existing evidence
components for five plain-language sections. No LLM participates in scoring or creates
facts. See CONTEXT_AWARE_VERIFICATION_REPORT.md for observed results and limitations.


## Reliable workspace additions

case_intake composes existing add_text_source/add_file_source with batch limits,
per-source failures and review state. case_report maps the owned stored snapshot
into the existing PDF generator. investigator_context projects canonical claims,
evidence, comparisons and availability for deterministic scan/case chat; it does not
extract or rescan content. fee_policy_scope adds conservative category/stage/condition
rules; missing scope never becomes an established match. React Flow graphOverview is
a display projection with all underlying node/edge records retained for inspection.
No new database tables, dependencies, model or parallel investigation engine.


## Role-aware organizer/program reasoning

organization_roles separates organizer/employer/provider names from claimed partners,
certificate associations, explicit issuers, domain-owner claims and payees. The
organization compatibility API returns primary names only. Existing scanning,
case extraction, canonical chat and reports use these records. program_claims retains
explicit ranges, assistance-promise scope and unpriced disclosures; program_graph
adds cited overview concepts without inventing affiliations. Default program graph
projection keeps key concepts readable; original nodes/edges remain available.
Analyze embeds the same CaseIntake used by Cases and calls the existing API. React
Flow now receives initial node dimensions and measured/resize-aware fitting.
Dashboard categories remain stored CommunityReport aggregation with explicit demo
and report-source metadata. No scoring authority is delegated to a model.
