"""Native OCR with explicit failure causes; filenames are metadata only."""
import io
from PIL import Image, ImageEnhance, ImageFilter


def preprocess_image(image_bytes: bytes) -> Image.Image:
    image=Image.open(io.BytesIO(image_bytes))
    image.load()
    if image.mode != 'RGB': image=image.convert('RGB')
    return ImageEnhance.Contrast(image).enhance(1.8).filter(ImageFilter.SHARPEN)


def extract_text_from_image(image_bytes: bytes, filename: str = 'upload.png') -> dict:
    result={'extracted_text':'','ocr_engine':'Tesseract','bounding_boxes':[],
            'character_count':0,'status':'UNAVAILABLE','error_code':None,'reason':''}
    try:
        image=preprocess_image(image_bytes)
    except Exception:
        return {**result,'error_code':'OCR_INVALID_IMAGE','reason':'Image decoding failed; no OCR or scanners ran.'}
    try:
        import pytesseract
        text=pytesseract.image_to_string(image, timeout=20)
    except ImportError:
        return {**result,'error_code':'OCR_DEPENDENCY_MISSING','reason':'Python OCR dependency is unavailable.'}
    except Exception as exc:
        # No exception messages containing document contents or local paths escape.
        name=type(exc).__name__
        code='OCR_ENGINE_MISSING' if name=='TesseractNotFoundError' else 'OCR_TIMEOUT' if isinstance(exc,RuntimeError) and 'timeout' in str(exc).lower() else 'OCR_ENGINE_ERROR'
        return {**result,'error_code':code,'reason':{'OCR_ENGINE_MISSING':'Native Tesseract is not installed or not on PATH.',
            'OCR_TIMEOUT':'OCR exceeded the 20 second limit.','OCR_ENGINE_ERROR':'OCR engine failed to extract text.'}[code]}
    if not text.strip():
        return {**result,'status':'EMPTY','error_code':'OCR_NO_TEXT','reason':'OCR completed but detected no readable text. Correct or enter the text before investigating.'}
    if len(text)>50000:
        return {**result,'error_code':'OCR_TEXT_TOO_LONG','reason':'Extracted text exceeds 50,000 characters; use a smaller image.'}
    return {**result,'status':'SUCCESS','extracted_text':text,'character_count':len(text),'reason':'Review and correct extracted text before investigation.'}
