import asyncio
import hashlib
from pathlib import PurePath
import jwt
from fastapi import HTTPException
from app.core.config import settings
from app.core.security import create_access_token, decode_access_token
from app.security.file_validator import validate_uploaded_file
from app.security.redaction import redact_sensitive_credentials
from app.ocr.ocr_engine import extract_text_from_image


async def extract_screenshot(file) -> dict:
    data=await file.read(settings.MAX_UPLOAD_SIZE_BYTES+1)
    valid,category,message=validate_uploaded_file(data,file.filename)
    if not valid or category!='screenshot':
        raise HTTPException(400,{'stage':'upload','code':'INVALID_IMAGE_UPLOAD','message':message if not valid else 'Expected an image file'})
    result=await asyncio.to_thread(extract_text_from_image,data,file.filename or 'upload.png')
    # Filename stays in signed metadata and display, never in an organization claim.
    filename=PurePath((file.filename or 'upload.png').replace('\\','/')).name[:255]
    result['extracted_text']=redact_sensitive_credentials(result['extracted_text'])
    result['character_count']=len(result['extracted_text'])
    claims={'purpose':'ocr_review','file_hash':hashlib.sha256(data).hexdigest(),
        'text_hash':hashlib.sha256(result['extracted_text'].encode()).hexdigest(),
        'filename':filename,'ocr_engine':result['ocr_engine'],'ocr_status':result['status']}
    from datetime import datetime,timedelta,timezone
    claims['exp']=datetime.now(timezone.utc)+timedelta(minutes=30)
    token=jwt.encode(claims,settings.JWT_SECRET,algorithm=settings.ALGORITHM)
    return {**result,'review_token':token,'filename':filename}


def reviewed_metadata(token: str, content: str) -> dict:
    claims=decode_access_token(token)
    if not claims or claims.get('purpose')!='ocr_review':
        raise HTTPException(422,{'stage':'ocr_review','code':'INVALID_REVIEW_TOKEN','message':'Extraction review expired or is invalid. Extract the image again.'})
    return {'filename':claims['filename'],'file_hash':claims['file_hash'],
        'ocr_engine':claims['ocr_engine'],'ocr_status':claims['ocr_status'],
        'original_ocr_text_hash':claims['text_hash'],
        'user_corrected': hashlib.sha256(redact_sensitive_credentials(content).encode()).hexdigest()!=claims['text_hash'],
        'content_origin':'USER_REVIEWED_OCR','reviewed':True}
