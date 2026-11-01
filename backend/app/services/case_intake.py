"""Batch composition of existing source ingestion, retaining per-source failures/review."""
from collections import Counter
from fastapi import HTTPException
from pydantic import BaseModel,Field
from typing import Literal
from app.core.config import settings
from app.models.all_models import InvestigationSource

class IntakeSource(BaseModel):
    input_type:Literal['text','url','email','phone']
    content:str=Field(min_length=1,max_length=50000)
    title:str|None=Field(default=None,max_length=200)
class IntakePayload(BaseModel):
    expected_revision:int=Field(ge=1)
    sources:list[IntakeSource]=Field(default_factory=list,max_length=25)

def enforce_source_limits(db,case,kinds):
    rows=db.query(InvestigationSource).filter_by(case_id=case.id,removed_at=None).all()
    counts=Counter(s.input_type for s in rows);counts.update(kinds)
    if sum(counts.values())>25:raise HTTPException(422,'A case supports at most 25 active sources')
    for kind,limit in [('screenshot',5),('url',max(1,settings.CASE_MAX_URLS)),('pdf',max(1,settings.CASE_MAX_PDFS))]:
        if counts[kind]>limit:raise HTTPException(422,f'A case supports at most {limit} active {kind} sources; remove a source before adding another')

async def intake_sources(db,case,payload,files):
    from app.services import case_service as service
    from app.schemas.cases import CaseSourceCreate
    if case.revision!=payload.expected_revision:raise HTTPException(409,'Case changed; reload before adding evidence')
    if not payload.sources and not files:raise HTTPException(422,'Supply at least one source')
    # Client extensions select the extraction route; the existing byte validators
    # still decide whether the uploaded content is valid for that route.
    kinds=['pdf' if (f.filename or '').lower().endswith('.pdf') else 'screenshot' for f in files]
    enforce_source_limits(db,case,[s.input_type for s in payload.sources]+kinds)
    for s in payload.sources:
        if not s.content.strip():raise HTTPException(422,'Source text cannot be blank')
    result=case.assessment
    for s in payload.sources:
        try:
            result=await service.add_text_source(db,case,CaseSourceCreate(**s.model_dump(),expected_revision=case.revision))
        except HTTPException as exc:
            if exc.status_code==409:raise
            db.rollback();db.refresh(case)
            source=service.begin_source(db,case,case.revision,s.input_type,s.title,s.content)
            result=service.fail_source(db,source,'SOURCE_VALIDATION_FAILED','Source could not be processed: invalid input or unsafe URL. No retrieval or verification was performed.')
    for f,kind in zip(files,kinds):
        result=await service.add_file_source(db,case,case.revision,kind,f)
    return result
