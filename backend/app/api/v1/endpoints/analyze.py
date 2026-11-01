from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.config import settings
from app.core.access import current_actor
from app.models.all_models import User
from app.models.all_models import Scan, ScanEvidence, RiskIndicator, VerificationResult
from app.schemas.all_schemas import ScanDetailResponse, ScanCreateRequest, ScreenshotExtractionResponse, ReviewedScreenshotRequest
from app.services.scan_service import execute_full_scan
from app.ocr.ocr_engine import extract_text_from_image
from app.documents.pdf_analyzer import analyze_pdf_document
from app.security.file_validator import validate_uploaded_file

router = APIRouter(prefix="/analyze", tags=["Analyze Engine"])

async def _persist_and_format_scan(
    db: Session, input_type: str, content: str,
    target_identifier: Optional[str] = None, extracted_metadata: Optional[dict] = None,
    synthetic: bool = False, user_id: Optional[str] = None,
    scan_id: Optional[str] = None, commit: bool = True,
    perform_research: bool = True, use_llm: bool = True
) -> ScanDetailResponse:
    from app.security.redaction import redact_sensitive_credentials
    from app.services.investigation_store import save_state, scan_response
    if not content.strip():
        raise HTTPException(422, "No readable text extracted; supply text or install Tesseract for OCR")
    content = redact_sensitive_credentials(content)
    scan_options = {"synthetic": synthetic}
    if not perform_research: scan_options["perform_research"] = False
    if not use_llm: scan_options["use_llm"] = False
    scan_result = await execute_full_scan(input_type, content, target_identifier, extracted_metadata, **scan_options)
    new_scan = Scan(input_type=input_type, input_content=content[:50000], user_id=user_id,
        target_identifier=target_identifier or scan_result.get("primary_domain") or "General Submission",
        status="COMPLETED", trust_score=scan_result["trust_score"], risk_level=scan_result["risk_level"],
        analysis_confidence=scan_result["analysis_confidence"], summary=scan_result["summary"], is_demo=synthetic)
    if scan_id:
        new_scan.id = scan_id
    db.add(new_scan)
    db.flush()
    state = scan_result["investigation"]
    state['source_id']=new_scan.id
    from app.services.case_claims import extract_claims
    state['claims']=extract_claims(new_scan.id,content,input_type)
    for ev in state["evidence"]:
        ev['source_id']=new_scan.id
        # Canonical investigation IDs are retained in the snapshot; legacy rows keep
        # their own globally unique primary keys for backwards-compatible queries.
        db.add(ScanEvidence(scan_id=new_scan.id, category=ev["category"], severity=ev["severity"],
            evidence=ev["evidence"], source=ev["source"], confidence=ev["confidence"], explanation=ev["explanation"]))
    for chk in scan_result["verification_results"]:
        db.add(VerificationResult(scan_id=new_scan.id, **chk))
    from app.models.all_models import AuditLog
    db.add(AuditLog(user_id=user_id, action="SCAN_COMPLETED", details={"scan_id": new_scan.id, "synthetic": synthetic}))
    from app.agents.investigation_orchestrator import refresh_investigation
    state=refresh_investigation(state)
    save_state(db, new_scan, state)
    if commit: db.commit()
    else: db.flush()
    return ScanDetailResponse(**(await scan_response(db, new_scan.id)))

@router.post("/url", response_model=ScanDetailResponse)
async def analyze_url_endpoint(req: ScanCreateRequest, db: Session = Depends(get_db), actor: Optional[User] = Depends(current_actor)):
    return await _persist_and_format_scan(
        db=db,
        input_type="url",
        content=req.content,
        target_identifier=req.target_identifier, user_id=actor.id if actor else None
    )

@router.post("/text", response_model=ScanDetailResponse)
async def analyze_text_endpoint(req: ScanCreateRequest, db: Session = Depends(get_db), actor: Optional[User] = Depends(current_actor)):
    return await _persist_and_format_scan(
        db=db,
        input_type="text",
        content=req.content,
        target_identifier=req.target_identifier, user_id=actor.id if actor else None
    )

@router.post("/email", response_model=ScanDetailResponse)
async def analyze_email_endpoint(req: ScanCreateRequest, db: Session = Depends(get_db), actor: Optional[User] = Depends(current_actor)):
    return await _persist_and_format_scan(
        db=db,
        input_type="email",
        content=req.content,
        target_identifier=req.target_identifier, user_id=actor.id if actor else None
    )

@router.post("/phone", response_model=ScanDetailResponse)
async def analyze_phone_endpoint(req: ScanCreateRequest, db: Session = Depends(get_db), actor: Optional[User] = Depends(current_actor)):
    return await _persist_and_format_scan(
        db=db,
        input_type="phone",
        content=req.content,
        target_identifier=req.target_identifier, user_id=actor.id if actor else None
    )

@router.post("/organization", response_model=ScanDetailResponse)
@router.post("/organizations/verify", response_model=ScanDetailResponse)
async def analyze_org_endpoint(req: ScanCreateRequest, db: Session = Depends(get_db), actor: Optional[User] = Depends(current_actor)):
    return await _persist_and_format_scan(
        db=db,
        input_type="org",
        content=req.content,
        target_identifier=req.target_identifier or req.content, user_id=actor.id if actor else None
    )

@router.post("/screenshot/extract", response_model=ScreenshotExtractionResponse)
async def extract_screenshot_endpoint(file: UploadFile = File(...), actor=Depends(current_actor)):
    from app.services.screenshot_service import extract_screenshot
    return await extract_screenshot(file)


@router.post("/screenshot/reviewed", response_model=ScanDetailResponse)
async def investigate_reviewed_screenshot(req: ReviewedScreenshotRequest, db: Session = Depends(get_db), actor=Depends(current_actor)):
    from app.services.screenshot_service import reviewed_metadata
    metadata=reviewed_metadata(req.review_token, req.content)
    if not req.content.strip():
        raise HTTPException(422, {"stage":"ocr_review","code":"EMPTY_REVIEW_TEXT","message":"Enter readable text before investigating."})
    try:
        return await _persist_and_format_scan(db, "screenshot", req.content, req.target_identifier,
            extracted_metadata=metadata,user_id=actor.id if actor else None)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(500, {"stage":"forensics","code":"SCANNER_ERROR","message":"Text review completed, but forensic investigation failed. Retry the investigation."})


@router.post("/screenshot", response_model=ScanDetailResponse)
@router.post("/image", response_model=ScanDetailResponse)
async def analyze_screenshot_endpoint(file: UploadFile = File(...), target_identifier: Optional[str] = Form(None),
    db: Session = Depends(get_db), actor=Depends(current_actor)):
    from app.services.screenshot_service import extract_screenshot, reviewed_metadata
    result=await extract_screenshot(file)
    if result['status']!='SUCCESS':
        raise HTTPException(422, {"stage":"ocr","code":result['error_code'],"message":result['reason']})
    metadata=reviewed_metadata(result['review_token'],result['extracted_text'])
    metadata.update(reviewed=False,content_origin="OCR_EXTRACTION")
    try:
        return await _persist_and_format_scan(db,"screenshot",result['extracted_text'],target_identifier,
            extracted_metadata=metadata,user_id=actor.id if actor else None)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(500,{"stage":"forensics","code":"SCANNER_ERROR","message":"OCR completed, but forensic investigation failed."})

@router.post("/pdf", response_model=ScanDetailResponse)
async def analyze_pdf_endpoint(
    file: UploadFile = File(...),
    target_identifier: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    actor: Optional[User] = Depends(current_actor)
):
    file_bytes = await file.read(settings.MAX_UPLOAD_SIZE_BYTES + 1)
    is_valid, category, msg = validate_uploaded_file(file_bytes, file.filename)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
        
    if category != "pdf":
        raise HTTPException(400, "Expected a PDF file")
    pdf_result = analyze_pdf_document(file_bytes, file.filename)
    if not pdf_result.get('num_pages') or not pdf_result.get('text','').strip():
        raise HTTPException(422,{'stage':'pdf_extraction','code':'PDF_NO_READABLE_TEXT','message':'PDF could not be parsed or contained no readable text. No forensic findings were generated.'})
    if len(pdf_result['text'])>50000:raise HTTPException(422,{'stage':'pdf_extraction','code':'PDF_TEXT_TOO_LONG','message':'PDF exceeds 50,000 extracted characters; split it into smaller sources.'})
    extracted_text = pdf_result["text"]
    
    return await _persist_and_format_scan(
        db=db,
        input_type="pdf",
        content=extracted_text,
        target_identifier=target_identifier,
        extracted_metadata=pdf_result, user_id=actor.id if actor else None
    )
