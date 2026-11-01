import os
import io
from typing import Tuple
from app.core.config import settings

# Magic byte signatures for authorized file types
MAGIC_NUMBERS = {
    "pdf": [b"%PDF"],
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "webp": [b"RIFF"], # WebP files start with RIFF....WEBP
}

class FileValidationError(Exception):
    pass

def validate_uploaded_file(file_bytes: bytes, filename: str) -> Tuple[bool, str, str]:
    """
    Validates uploaded file against:
    1. Size limit (max 10MB)
    2. File extension
    3. Magic byte inspection
    Returns (is_valid, sanitized_category, error_or_success_message)
    """
    if not file_bytes or len(file_bytes) == 0:
        return False, "unknown", "Uploaded file is empty"
        
    if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        return False, "unknown", f"File size exceeds 10MB limit ({len(file_bytes)} bytes)"
        
    # Check extension
    _, ext = os.path.splitext((filename or "").lower())
    if ext not in settings.ALLOWED_EXTENSIONS:
        return False, "unknown", f"Disallowed extension: '{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        
    ext_clean = ext.lstrip(".")
    
    # Text or email files
    if ext_clean in ["txt", "eml"]:
        # Verify valid UTF-8/ASCII without null bytes
        if b"\x00" in file_bytes[:1024]:
            return False, "text", "Binary content detected in text file"
        return True, "text" if ext_clean == "txt" else "email", "Valid text/email file"
        
    # Check magic bytes for binary files
    expected_signatures = MAGIC_NUMBERS.get(ext_clean)
    if expected_signatures:
        matched = False
        for sig in expected_signatures:
            if ext_clean != "webp" and file_bytes.startswith(sig):
                matched = True
                break
            if ext_clean == "webp" and file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP":
                matched = True
                break
        if not matched:
            return False, ext_clean, f"Magic bytes do not match expected signature for {ext_clean}"
            
    category = "pdf" if ext_clean == "pdf" else "screenshot"
    return True, category, f"File passed validation as {category}"

def validate_file_upload(file_bytes: bytes, filename: str) -> Tuple[bool, str]:
    """
    Test and convenience validation wrapper.
    Returns (is_valid, error_or_success_message).
    """
    is_valid, category, msg = validate_uploaded_file(file_bytes, filename)
    if not is_valid:
        if "exceeds" in msg.lower():
            return False, f"File exceeds maximum allowed size ({len(file_bytes)} bytes > 10MB limit)"
        if "magic byte" in msg.lower():
            return False, f"Magic byte signature mismatch: {msg}"
        return False, msg
    return True, msg
