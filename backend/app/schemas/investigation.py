"""Contracts shared by deterministic services and optional language providers."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    category: str
    severity: str
    evidence: str
    source: str
    confidence: float = Field(ge=0, le=1)
    explanation: str = ""
    timestamp: str
    observed_value: str
    origin: Literal["DIRECT_OBSERVATION", "DETERMINISTIC_RULE", "EXTERNAL_SOURCE", "SYNTHETIC"]
    verification_status: str = "NOT_INDEPENDENTLY_VERIFIED"
    correlation_group: str
    related_entities: list[str] = Field(default_factory=list)
    source_spans: list[dict] = Field(default_factory=list)


class ResearchSource(BaseModel):
    id: str
    title: str
    url: str
    extracted_information: str
    retrieved_at: str
    source_type: Literal["OFFICIAL_DOMAIN", "INDEPENDENT_SOURCE"]
    relevance: float = Field(ge=0, le=1)
    claim: str
    verification_status: str = "NOT_INDEPENDENTLY_VERIFIED"


class ResearchResult(BaseModel):
    status: Literal["COMPLETED", "SEARCH_UNAVAILABLE", "SEARCH_NOT_PERFORMED"]
    provider: str = "tavily"
    query: str = ""
    sources: list[ResearchSource] = Field(default_factory=list)
    reason: str = ""


class CitedInterpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=2000)
    evidence_ids: list[str] = Field(min_length=1, max_length=20)


class ExtractedClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=1000)
    quote: str = Field(min_length=1, max_length=1000)


class LanguageOutput(BaseModel):
    """No score, verdict, tools, verification flags, or newly asserted evidence."""
    model_config = ConfigDict(extra="forbid")
    interpretations: list[CitedInterpretation] = Field(default_factory=list, max_length=10)
    claims: list[ExtractedClaim] = Field(default_factory=list, max_length=10)


class Recommendation(BaseModel):
    action_id: str
    title: str
    reason: str
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    expected_outcomes: list[str]
    required_information: list[str]
    execution_type: Literal["AUTOMATED", "MANUAL"]
    status: Literal["AVAILABLE", "COMPLETED", "UNAVAILABLE"]
    ranking_score: int
    instructions: str
    unavailable_reason: str | None = None
