"""Bounded external evidence retrieval. Search snippets never authenticate an offer."""
import ipaddress
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid5, NAMESPACE_URL
import httpx
from pydantic import BaseModel, Field, ConfigDict
from app.core.config import settings
from app.schemas.investigation import ResearchResult, ResearchSource
from app.security.redaction import redact_sensitive_credentials


def safe_source_url(value: str) -> str | None:
    try:
        p = urlsplit(value)
        host = (p.hostname or "").lower().rstrip(".")
        if p.scheme not in {"https", "http"} or not host or p.username or p.password:
            return None
        if host == "localhost" or host.endswith((".local", ".internal", ".localhost", ".lan")):
            return None
        try:
            if not ipaddress.ip_address(host).is_global:
                return None
        except ValueError:
            if "." not in host:
                return None
        # Search URLs are citations only, never fetched. Strip fragments and queries.
        return urlunsplit((p.scheme, p.netloc, p.path, "", ""))
    except ValueError:
        return None


class TavilyItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str = Field(max_length=2000)
    url: str = Field(max_length=4000)
    content: str = Field(max_length=100000)
    score: float = Field(default=0, ge=0, le=1)


class TavilyService:
    def __init__(self, api_key: str | None = None, transport=None):
        self.api_key = settings.TAVILY_API_KEY if api_key is None else api_key
        self.transport = transport

    async def search(self, query: str, official_domains: list[str] | None = None) -> ResearchResult:
        if not self.api_key:
            return ResearchResult(status="SEARCH_UNAVAILABLE", reason="TAVILY_API_KEY is not configured")
        query = redact_sensitive_credentials(query)[:250]
        try:
            async with httpx.AsyncClient(timeout=settings.RESEARCH_TIMEOUT_SECONDS,
                    follow_redirects=False, transport=self.transport, trust_env=False) as client:
                res = await client.post("https://api.tavily.com/search",
                    headers={"Authorization": f"Bearer {self.api_key}"}, json={
                        "query": query, "search_depth": "basic", "max_results": 5,
                        "include_answer": False, "include_raw_content": False})
                res.raise_for_status()
                raw = res.json()
            if not isinstance(raw.get("results"), list):
                raise ValueError("Invalid search response")
            sources = []
            seen = set()
            for row in raw["results"][:5]:
                item = TavilyItem.model_validate(row)
                url = safe_source_url(item.url)
                if not url or url in seen:
                    continue
                seen.add(url)
                host = urlsplit(url).hostname
                official = any(host == d or host.endswith("." + d) for d in (official_domains or []))
                sources.append(ResearchSource(
                    id=str(uuid5(NAMESPACE_URL, url)), title=redact_sensitive_credentials(item.title), url=url,
                    extracted_information=redact_sensitive_credentials(item.content)[:4000],
                    retrieved_at=datetime.now(timezone.utc).isoformat(),
                    source_type="OFFICIAL_DOMAIN" if official else "INDEPENDENT_SOURCE",
                    relevance=item.score, claim=query,
                    # Host classification is not factual confirmation of snippet contents.
                    verification_status="NOT_INDEPENDENTLY_VERIFIED"))
            sources.sort(key=lambda x: (x.source_type != "OFFICIAL_DOMAIN", -x.relevance))
            return ResearchResult(status="COMPLETED", query=query, sources=sources,
                reason="Retrieved search excerpts; sender and offer remain unverified. No matches is not proof of safety.")
        except Exception:
            return ResearchResult(status="SEARCH_UNAVAILABLE", query=query,
                reason="Tavily request failed or response validation failed")
