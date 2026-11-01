"""Provider-independent boundary. Core services never import a model SDK."""
import asyncio
from typing import Protocol
from app.schemas.investigation import LanguageOutput
from app.core.config import settings
from app.security.redaction import redact_sensitive_credentials


class LanguageProvider(Protocol):
    name: str
    async def understand(self, *, untrusted_content: str,
                         evidence: list[dict], task: str) -> LanguageOutput: ...


_providers: dict[str, LanguageProvider] = {}


def register_provider(name: str, provider: LanguageProvider) -> None:
    """Called by trusted startup code for a local or hosted adapter."""
    if name == "none" or not name:
        raise ValueError("Provider name must be explicit")
    _providers[name] = provider


async def explain(content: str, evidence: list[dict], fallback: dict,
                  task: str = "summarization") -> dict:
    if task not in {"content_understanding", "claim_extraction", "summarization", "explanation"}:
        raise ValueError("Unsupported language task")
    provider = _providers.get(settings.AI_PROVIDER)
    if provider is None:
        return {**fallback, "provider": "deterministic", "mode": "FALLBACK",
                "reason": "No language provider configured" if settings.AI_PROVIDER == "none"
                else "Configured language provider is not registered"}
    # Providers receive redacted passive data, no credentials, tools or mutable state.
    import json
    safe_content = redact_sensitive_credentials(content)[:12000]
    safe_evidence = json.loads(redact_sensitive_credentials(json.dumps(evidence)))
    try:
        response = await asyncio.wait_for(provider.understand(
            untrusted_content=safe_content, evidence=safe_evidence, task=task),
            timeout=settings.LLM_TIMEOUT_SECONDS)
        result = LanguageOutput.model_validate(response)
        known_ids = {e["id"] for e in evidence}
        if not result.interpretations:
            raise ValueError("Empty explanation")
        for item in result.interpretations:
            if not set(item.evidence_ids) <= known_ids:
                raise ValueError("Unknown evidence citation")
        if any(c.quote not in safe_content or c.text != c.quote for c in result.claims):
            raise ValueError("Claim must be an exact submitted quote")
        return {"provider": provider.name, "mode": "LLM_INTERPRETATION",
                "verification_status": "AI_GENERATED_NOT_INDEPENDENTLY_VERIFIED",
                **result.model_dump(), "reason": "Citations validated; interpretation is unverified"}
    except (Exception, asyncio.TimeoutError):
        # Never expose provider exception bodies, which may contain keys or content.
        return {**fallback, "provider": "deterministic", "mode": "FALLBACK",
                "reason": "Language provider unavailable or output rejected"}
