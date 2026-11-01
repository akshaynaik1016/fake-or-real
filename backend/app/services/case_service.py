import asyncio
import hashlib
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import PurePath
from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.models.all_models import InvestigationCase,InvestigationSource,ExtractedClaim,CrossSourceFinding,CaseAssessmentRevision,Scan
from app.services.case_claims import extract_claims
from app.services.case_assessment import assess_case
from app.security.redaction import redact_sensitive_credentials
from app.core.config import settings

from app.services.case_intake import enforce_source_limits

MAX_SOURCES=25

def owned_case(db,case_id,actor=None):
    case=db.get(InvestigationCase,case_id)
    if case is None or (actor is not None and actor.role!='ADMIN' and case.user_id!=actor.id):raise HTTPException(404,'Case not found')
    return case


def source_dict(source):
    return {key:getattr(source,key) for key in ['id','case_id','title','input_type','submitted_content','extracted_text','filename',
        'processing_status','extraction_status','error_code','error_message','content_hash','metadata_json','scan_id','analysis']} | {
        'created_at':source.created_at.replace(tzinfo=timezone.utc).isoformat(),'removed_at':source.removed_at.isoformat() if source.removed_at else None}


def claim_dict(claim):
    return {key:getattr(claim,key) for key in ['id','source_id','claim_type','value','normalized_value','excerpt','location','extraction_method','verification_status']}


def record_revision(db,case,event,expected=None,last_action=None,running_action='keep'):
    db.flush()
    locked=db.query(InvestigationCase).filter_by(id=case.id).populate_existing().with_for_update().one()
    if expected is not None and locked.revision!=expected:
        db.rollback();raise HTTPException(409,'Case changed; reload before editing')
    previous=locked.revision
    changed=db.execute(update(InvestigationCase).where(InvestigationCase.id==case.id,InvestigationCase.revision==previous).values(revision=previous+1))
    if changed.rowcount!=1:
        db.rollback();raise HTTPException(409,'Case changed concurrently; reload')
    db.refresh(locked)
    rows=db.query(InvestigationSource).filter_by(case_id=case.id,removed_at=None).order_by(InvestigationSource.created_at,InvestigationSource.id).all()
    sources=[source_dict(s) for s in rows];ids=[s.id for s in rows if s.processing_status=='READY']
    claims=[claim_dict(c) for c in db.query(ExtractedClaim).filter(ExtractedClaim.source_id.in_(ids)).order_by(ExtractedClaim.source_id,ExtractedClaim.id).all()] if ids else []
    snapshot=assess_case(locked,sources,claims)
    if last_action:snapshot['last_action']=last_action
    pending=locked.assessment.get('running_action') if running_action=='keep' else running_action
    if pending:
        snapshot['running_action']=pending
        for action in snapshot['recommendations']:
            if action['execution_type']=='AUTOMATED' and action['status']!='COMPLETED':
                action.update(status='UNAVAILABLE',unavailable_reason='Another case check is running.')
    db.query(CrossSourceFinding).filter_by(case_id=case.id).update({'active':False})
    for finding in snapshot['cross_source_findings']:
        row=db.get(CrossSourceFinding,finding['id'])
        if row is None:row=CrossSourceFinding(id=finding['id'],case_id=case.id);db.add(row)
        for key in ['kind','classification','severity','description','citations']:setattr(row,key,deepcopy(finding[key]))
        row.active=True
    locked.status=snapshot['status'];locked.assessment=deepcopy(snapshot)
    db.add(CaseAssessmentRevision(case_id=case.id,revision=locked.revision,event=event,snapshot=deepcopy(snapshot)))
    db.commit()
    return snapshot


def create_case(db,title,actor):
    case=InvestigationCase(title=title.strip(),user_id=actor.id if actor else None)
    if not case.title:raise HTTPException(422,'Case title cannot be blank')
    db.add(case);db.flush();return record_revision(db,case,'CASE_CREATED',expected=0)


def begin_source(db,case,expected,input_type,title,submitted='',filename=None):
    enforce_source_limits(db,case,[input_type])
    if db.query(InvestigationSource).filter_by(case_id=case.id,removed_at=None).count()>=MAX_SOURCES:raise HTTPException(422,'A case supports at most 25 active sources')
    source=InvestigationSource(case_id=case.id,input_type=input_type,title=(title or filename or input_type.title()+' source')[:200],
        submitted_content=redact_sensitive_credentials(submitted),filename=filename)
    db.add(source);db.flush()
    record_revision(db,case,'SOURCE_ADDED:'+source.id,expected)
    return source


def fail_source(db,source,code,message,extraction='FAILED'):
    db.flush()
    db.refresh(source)
    if source.removed_at:return owned_case(db,source.case_id).assessment
    source.processing_status='FAILED';source.extraction_status=extraction;source.error_code=code;source.error_message=message
    source.analysis={}
    return record_revision(db,owned_case(db,source.case_id),'SOURCE_FAILED:'+source.id)


async def process_source(db,source,content,metadata=None):
    from app.api.v1.endpoints.analyze import _persist_and_format_scan
    db.flush()
    db.refresh(source)
    if source.removed_at:return owned_case(db,source.case_id).assessment
    text=redact_sensitive_credentials(content)
    if not text.strip():return fail_source(db,source,'EMPTY_CONTENT','No readable source text is available.')
    try:
        case=owned_case(db,source.case_id)
        detail=await _persist_and_format_scan(db,source.input_type,text,extracted_metadata=metadata or source.metadata_json,
            user_id=case.user_id,commit=False,perform_research=False,use_llm=False)
        source.scan_id=detail.id;source.analysis=detail.investigation;source.extracted_text=text
        source.content_hash=hashlib.sha256(' '.join(text.casefold().split()).encode()).hexdigest()
        source.processing_status='READY'
        if source.extraction_status!='UNAVAILABLE':source.error_message=None;source.error_code=None
        db.query(ExtractedClaim).filter_by(source_id=source.id).delete()
        for claim in extract_claims(source.id,text,source.input_type,source.submitted_content):db.add(ExtractedClaim(**claim))
        return record_revision(db,case,'SOURCE_PROCESSED:'+source.id)
    except HTTPException:raise
    except Exception:
        db.rollback();return fail_source(db,source,'SCANNER_ERROR','Readable content is available, but the forensic scanners could not complete.',source.extraction_status)


async def add_text_source(db,case,req):
    from app.services.case_url_fetcher import validate_public_target,fetch_public_text,URLFetchError
    if not req.content.strip():raise HTTPException(422,'Source text cannot be blank')
    if req.input_type=='url':
        try:validate_public_target(req.content.strip(),resolve=False)
        except URLFetchError as exc:raise HTTPException(422,{'code':exc.code,'message':str(exc)})
    source=begin_source(db,case,req.expected_revision,req.input_type,req.title,req.content)
    content=source.submitted_content
    if req.input_type=='url':
        if settings.CASE_URL_FETCH_ENABLED:
            try:
                fetched=await fetch_public_text(content.strip());content=redact_sensitive_credentials(fetched.pop('text'))
                source.metadata_json={**fetched,'source_url':fetched['final_url']};source.extraction_status='SUCCESS'
            except URLFetchError as exc:return fail_source(db,source,exc.code,str(exc),'UNAVAILABLE')
        else:
            source.metadata_json={'source_url':content.strip(),'retrieval':'DISABLED'}
            source.extraction_status='UNAVAILABLE';source.error_code='URL_FETCH_DISABLED'
            source.error_message='URL page retrieval is disabled. Only the submitted URL structure is analyzed; page contents remain unknown.'
    else:source.extraction_status='SUCCESS'
    return await process_source(db,source,content)


async def add_file_source(db,case,expected,kind,file,title=None):
    filename=PurePath((file.filename or 'upload').replace('\\','/')).name[:255]
    source=begin_source(db,case,expected,kind,title,filename=filename)
    try:
        if kind=='screenshot':
            from app.services.screenshot_service import extract_screenshot
            result=await extract_screenshot(file)
            source.extracted_text=result['extracted_text'];source.extraction_status=result['status']
            source.metadata_json={'filename':filename,'ocr_engine':result['ocr_engine'],'ocr_status':result['status'],
                'original_text_hash':hashlib.sha256(result['extracted_text'].encode()).hexdigest()}
            if result['status']!='SUCCESS':return fail_source(db,source,result['error_code'],result['reason'],result['status'])
        else:
            from app.security.file_validator import validate_uploaded_file
            from app.documents.pdf_analyzer import analyze_pdf_document
            data=await file.read(settings.MAX_UPLOAD_SIZE_BYTES+1)
            valid,category,message=validate_uploaded_file(data,filename)
            if not valid or category!='pdf':return fail_source(db,source,'INVALID_PDF_UPLOAD',message)
            result=await asyncio.to_thread(analyze_pdf_document,data,filename)
            if not result.get('num_pages') or not result.get('text','').strip():return fail_source(db,source,'PDF_EXTRACTION_ERROR','PDF contained no readable text or could not be parsed.')
            if len(result['text'])>50000:return fail_source(db,source,'PDF_TEXT_TOO_LONG','PDF text exceeds 50,000 characters. Split the document.')
            source.extracted_text=redact_sensitive_credentials(result['text']);source.extraction_status='SUCCESS'
            source.metadata_json={'filename':filename,'parser':'pypdf','num_pages':result['num_pages'],
                'flags':result.get('flags',[]),'has_manipulation_indicators':result.get('has_manipulation_indicators',False)}
        source.processing_status='NEEDS_REVIEW'
        return record_revision(db,case,'EXTRACTION_READY:'+source.id)
    except HTTPException as exc:
        db.rollback();return fail_source(db,source,'UPLOAD_VALIDATION_ERROR',str(exc.detail))
    except Exception:
        db.rollback();return fail_source(db,source,'EXTRACTION_ERROR','Source extraction failed; no findings were fabricated.')


async def review_source(db,case,source,req):
    if source.input_type not in {'screenshot','pdf'}:raise HTTPException(400,'This source does not have an extraction review')
    text=redact_sensitive_credentials(req.content)
    if source.processing_status=='READY' and text==source.extracted_text:raise HTTPException(409,'This text is already processed; no duplicate scan was created')
    if not text.strip():raise HTTPException(422,'Reviewed text cannot be empty')
    metadata=deepcopy(source.metadata_json)
    metadata.update(reviewed=True,content_origin='USER_REVIEWED_EXTRACTION',
        user_corrected=hashlib.sha256(text.encode()).hexdigest()!=metadata.get('original_text_hash',hashlib.sha256(source.extracted_text.encode()).hexdigest()))
    source.metadata_json=metadata;source.processing_status='PROCESSING'
    record_revision(db,case,'SOURCE_REVIEWED:'+source.id,req.expected_revision)
    return await process_source(db,source,text,metadata)


def remove_source(db,case,source,expected):
    source.removed_at=datetime.now(timezone.utc);source.processing_status='REMOVED'
    return record_revision(db,case,'SOURCE_REMOVED:'+source.id,expected)


async def execute_case_action(db,case,action_id,expected):
    if case.assessment.get('running_action'):raise HTTPException(409,'Another case check is running')
    action=next((r for r in case.assessment.get('recommendations',[]) if r['action_id']==action_id),None)
    if not action or action['execution_type']!='AUTOMATED':raise HTTPException(400,'Only a recommended automated check can run')
    if case.revision!=expected:raise HTTPException(409,'Case changed; reload')
    if action['status']=='COMPLETED':return case.assessment
    if action['status']!='AVAILABLE':raise HTTPException(409,action.get('unavailable_reason') or 'Check unavailable')
    if action_id in {'official_listing','verify_notice'}:case.research_calls+=1
    record_revision(db,case,'CHECK_STARTED:'+action_id,expected,running_action={'action_id':action_id,'started_at':datetime.now(timezone.utc).isoformat()})
    try:
        if action_id.startswith('sender:'):
            from app.services.investigation_execution import execute_recommendation
            source=db.get(InvestigationSource,action_id.split(':',1)[1])
            if not source or source.case_id!=case.id or source.removed_at:raise HTTPException(404,'Source not available')
            state=await execute_recommendation(db,db.get(Scan,source.scan_id),'verify_sender_domain',source.analysis['revision'])
            db.refresh(source)
            if source.removed_at:return record_revision(db,case,'CHECK_SOURCE_REMOVED',last_action={
                'action_id':action_id,'status':'UNAVAILABLE','message':'The source was removed while this check ran; its findings were excluded.'},running_action=None)
            source.analysis=deepcopy(state);status=state.get('last_change',{}).get('status','COMPLETED')
            message=state.get('last_change',{}).get('reason','Existing sender reference check inspected.')
        elif action_id=='verify_notice':
            from app.services.notice_verification import retrieve_notice
            result=await retrieve_notice(case.assessment['claims'])
            db.refresh(case)
            case.research_results=[*case.research_results,result]
            status='COMPLETED' if result['status']=='COMPLETED' else 'UNAVAILABLE';message=result['reason']
        else:
            from app.integrations.web_research.tavily_service import TavilyService
            from app.agents.investigation_orchestrator import organization_reference
            org=next(c['value'] for c in case.assessment['claims'] if c['claim_type']=='organization')
            reference=organization_reference(org) or {}
            result=await TavilyService().search(org[:100]+' official internship careers recruitment listing',reference.get('official_domains',[]))
            db.refresh(case)
            case.research_results=[*case.research_results,{**result.model_dump(),'organization':org}]
            status='COMPLETED' if result.status=='COMPLETED' else 'UNAVAILABLE';message=result.reason
        return record_revision(db,case,'CHECK_FINISHED:'+action_id,last_action={'action_id':action_id,'status':status,'message':message},running_action=None)
    except Exception as exc:
        db.rollback()
        return record_revision(db,owned_case(db,case.id),'CHECK_UNAVAILABLE:'+action_id,last_action={
            'action_id':action_id,'status':'UNAVAILABLE','message':str(exc.detail) if isinstance(exc,HTTPException) else 'Check could not complete; no verification was fabricated.'},running_action=None)
