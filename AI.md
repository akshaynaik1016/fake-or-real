# Investigation and language-provider boundaries

## Core engine

`scan_service.execute_full_scan` retains the existing scanners and weighted trust
score. `agents/investigation_orchestrator.py` performs a fixed bounded workflow:
normalize evidence → extract submitted entities deterministically → optional Tavily
research → optional language interpretation → fusion → graph → recommendations.
No language-model tool calls or autonomous agent loop exist. LangChain is not
required or installed. The workflow is directly testable with no network/model.

The existing `answer_investigator_query` remains the conversational fallback and
now uses stored evidence rather than rerunning scans or fabricating missing scan
contexts. Its responses identify deterministic/fallback mode and return cited IDs.

## Provider-independent interface

`integrations/llm/provider.py` defines:

```python
class LanguageProvider(Protocol):
    name: str
    async def understand(self, *, untrusted_content: str,
                         evidence: list[dict], task: str) -> LanguageOutput: ...
```

Trusted application startup code can register an implementation:

```python
register_provider("my-provider", MyLanguageAdapter())
# Select AI_PROVIDER=my-provider in the server environment.
```

An adapter must separate system instructions from passive user/document content,
request structured JSON, prohibit tools, avoid logging content/keys, and validate
`LanguageOutput`. It must not install or load models during core startup. Adapter
credentials and endpoints belong in server-side configuration. A future local or
hosted implementation can add its own timeout, model name and connection handling
without changing scanners, fusion or persistence.

The central boundary redacts credentials, sends copies, bounds content and output,
and enforces an eight-second default timeout. Output accepts only interpretations
with known evidence IDs and verbatim claims with exact source quotes. Extra fields
such as `risk_score`, verdicts, verification flags, evidence records or tool commands
are rejected. Citation validation does not prove that a paraphrase is true: all
model interpretations stay `AI_GENERATED_NOT_INDEPENDENTLY_VERIFIED` and cannot
write evidence, scores, research plans, entity relations or verification status.

With no registered provider, or on timeout/error/malformed output, the deterministic
summary is returned with a reason and `provider=deterministic`, `mode=FALLBACK`.
No output is described as Gemma output unless a future Gemma adapter actually ran.
Gemma/Ollama and hosted SDK integrations are intentionally deferred.

## Evidence Fusion assumptions

`bayesian_evidence_engine.py` is independently testable. Default **HEURISTIC** mode
uses log-odds updates with prior 0.25 and severity multipliers: critical 8, high 3,
moderate 1.6, low 1.1, verified 0.8. A finding's heuristic reliability exponent scales
the multiplier. These are policy assumptions, not empirical scam probabilities.

Only the strongest absolute log update in each correlation group contributes.
Payment-language findings share the payment group; credential-language findings
share sensitive-data; related domain observations share infrastructure; lookalike
and organization/sender-reference comparisons share identity. This conservative
rule reduces duplicated signals but does not model every cross-group dependency.
Opposing observations are retained and reduce confidence when they conflict in a
group. Unavailable, historical unknown, synthetic and unverified external evidence
contribute nothing. Missing checks never become safety evidence.

Optional `FusionConfig` likelihood ratios require a calibration reference. BAYESIAN
mode is used only if supplied ratios cover every eligible category; otherwise the
whole calculation stays heuristic. No calibrated dataset ships with the project.
The interface supports future calibration but does not validate the caller's dataset.

Risk classification thresholds: score ≥80 critical, ≥60 high, ≥35 moderate, otherwise
low. Sparse evidence yields INSUFFICIENT_INFORMATION; no eligible evidence yields a
null risk score. Risk is distinct from evidence confidence (independent grouped
observations and reliability) and coverage (completed checks / expected checks).
The legacy Trust Score has the opposite direction: higher means fewer concerns.
It remains visibly labelled as a legacy uncalibrated baseline.


## Monetary and OCR provenance update

The deterministic payment scanner emits monetary roles, categories, periods and
exact source spans, separating compensation from local fee demands. Ambiguous
amounts never borrow a stipend amount. These are scanner observations, not LLM output.
User-reviewed OCR text is explicit input with file/extraction hashes and correction
metadata; filenames have no automatic identity-claim role. No new model dependency
or scoring authority is introduced by these accuracy/usability fixes.
