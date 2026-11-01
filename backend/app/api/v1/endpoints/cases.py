from typing import Literal
from datetime import timezone
from fastapi import APIRouter,Depends,HTTPException,UploadFile,File,Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.access import current_actor
from app.models.all_models import InvestigationCase,InvestigationSource,CaseAssessmentRevision
from app.schemas.cases import CaseCreate,CaseMutation,CaseSourceCreate,CaseSourceReview,CaseRename
from app.services import case_service as service
router=APIRouter(prefix='/cases',tags=['Multi-source cases'])

@router.get('')
def list_cases(db:Session=Depends(get_db),actor=Depends(current_actor)):
    query=db.query(InvestigationCase)
    if actor and actor.role!='ADMIN':query=query.filter_by(user_id=actor.id)
    return [{'id':c.id,'title':c.title,'status':c.status,'revision':c.revision,'fusion':c.assessment.get('fusion',{}),
        'source_count':len(c.assessment.get('sources',[])),'updated_at':c.updated_at.replace(tzinfo=timezone.utc)} for c in query.order_by(InvestigationCase.updated_at.desc()).limit(100)]

@router.post('')
def create_case(req:CaseCreate,db:Session=Depends(get_db),actor=Depends(current_actor)):
    return service.create_case(db,req.title,actor)

@router.get('/{case_id}')
def get_case(case_id:str,db:Session=Depends(get_db),actor=Depends(current_actor)):
    return service.owned_case(db,case_id,actor).assessment

@router.patch('/{case_id}')
def rename_case(case_id:str,req:CaseRename,db:Session=Depends(get_db),actor=Depends(current_actor)):
    case=service.owned_case(db,case_id,actor)
    if not req.title.strip():raise HTTPException(422,'Case title cannot be blank')
    # Validate the revision before changing ORM state.
    if case.revision!=req.expected_revision:raise HTTPException(409,'Case changed; reload')
    case.title=req.title.strip();return service.record_revision(db,case,'CASE_RENAMED',req.expected_revision)

@router.post('/{case_id}/sources')
async def add_source(case_id:str,req:CaseSourceCreate,db:Session=Depends(get_db),actor=Depends(current_actor)):
    return await service.add_text_source(db,service.owned_case(db,case_id,actor),req)

@router.post('/{case_id}/sources/upload')
async def upload_source(case_id:str,file:UploadFile=File(...),input_type:Literal['screenshot','pdf']=Form(...),
    expected_revision:int=Form(...),title:str|None=Form(None),db:Session=Depends(get_db),actor=Depends(current_actor)):
    if title and len(title)>200:raise HTTPException(422,'Source title too long')
    return await service.add_file_source(db,service.owned_case(db,case_id,actor),expected_revision,input_type,file,title)

def source_in_case(db,case_id,source_id):
    source=db.get(InvestigationSource,source_id)
    if source is None or source.case_id!=case_id or source.removed_at:raise HTTPException(404,'Source not found')
    return source

@router.post('/{case_id}/sources/{source_id}/review')
async def review_source(case_id:str,source_id:str,req:CaseSourceReview,db:Session=Depends(get_db),actor=Depends(current_actor)):
    case=service.owned_case(db,case_id,actor)
    return await service.review_source(db,case,source_in_case(db,case_id,source_id),req)

@router.delete('/{case_id}/sources/{source_id}')
def remove_source(case_id:str,source_id:str,req:CaseMutation,db:Session=Depends(get_db),actor=Depends(current_actor)):
    case=service.owned_case(db,case_id,actor)
    return service.remove_source(db,case,source_in_case(db,case_id,source_id),req.expected_revision)

@router.get('/{case_id}/revisions')
def revisions(case_id:str,db:Session=Depends(get_db),actor=Depends(current_actor)):
    service.owned_case(db,case_id,actor)
    return [{'revision':r.revision,'event':r.event,'created_at':r.created_at.replace(tzinfo=timezone.utc),'fusion':r.snapshot['fusion']} for r in db.query(CaseAssessmentRevision).filter_by(case_id=case_id).order_by(CaseAssessmentRevision.revision.desc()).limit(200)]

@router.get('/{case_id}/revisions/{revision}')
def revision(case_id:str,revision:int,db:Session=Depends(get_db),actor=Depends(current_actor)):
    service.owned_case(db,case_id,actor)
    row=db.query(CaseAssessmentRevision).filter_by(case_id=case_id,revision=revision).first()
    if not row:raise HTTPException(404,'Revision not found')
    return row.snapshot

@router.post('/{case_id}/actions/{action_id}')
async def action(case_id:str,action_id:str,req:CaseMutation,db:Session=Depends(get_db),actor=Depends(current_actor)):
    return await service.execute_case_action(db,service.owned_case(db,case_id,actor),action_id,req.expected_revision)
