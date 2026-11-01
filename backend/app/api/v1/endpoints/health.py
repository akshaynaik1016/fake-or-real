from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "fake-or-real-api",
        "version": "1.0.0"
    }

@router.get("/ready")
def readiness_check():
    import shutil
    from sqlalchemy import text
    from app.core.database import engine
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        connected = True
    except Exception:
        connected = False
    return {"ready": connected, "database": "CONNECTED" if connected else "UNAVAILABLE",
        "scoring_engine": "READY", "language_provider_required": False,
        "ocr_engine": "AVAILABLE" if shutil.which("tesseract") else "UNAVAILABLE",
        "external_research": "OPTIONAL"}
