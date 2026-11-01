# Implementation plan

1. Audit existing modules and run baseline tests/build in isolated dependencies.
2. Preserve scanners; fix fabricated evidence, unsafe configuration and missing
   verification states. Preserve the legacy weighted score as a labelled baseline.
3. Add validated evidence/research/LLM contracts and a provider registry. Default
   to deterministic explanation. LLM output has no score or evidence-writing path.
4. Implement bounded Tavily HTTP search, transparent heuristic fusion with optional
   supplied calibrated likelihood ratios, correlation groups and missing coverage.
5. Construct TrustGraph from extracted observations and evidence. Rank explicit
   follow-up actions and execute allowed checks with persistence and history.
6. Integrate snapshot persistence via additive versioned migration. Existing scan
   records remain readable without rerunning network scans. Wire current result UI,
   report and investigator to the same stored evidence.
7. Run existing/new regression tests, type checking, build and offline end-to-end
   smoke tests. Document exact results, API changes, demo and remaining limitations.

Provider-specific models and LangChain integration are deferred; neither is needed
for deterministic core completion. A future adapter implements the provider protocol
without changing the investigation engine.
