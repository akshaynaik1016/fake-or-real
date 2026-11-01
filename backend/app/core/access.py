"""Authenticated ownership outside the explicitly local demo environment."""
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.security import decode_access_token
from app.models.all_models import User, Scan, SavedReport


async def current_actor(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("authorization", "")
    if not auth:
        if settings.ENVIRONMENT == "development" and settings.DEMO_MODE:
            return None
        raise HTTPException(401, "Authentication required")
    kind, _, token = auth.partition(" ")
    claims = decode_access_token(token) if kind.lower() == "bearer" else None
    user = db.get(User, claims.get("sub")) if claims else None
    if not user or not user.is_active:
        raise HTTPException(401, "Invalid or expired authentication")
    return user


async def enforce_access(request: Request, db: Session = Depends(get_db)):
    path = request.url.path
    public = {"/api/auth/register", "/api/auth/login", "/api/health", "/api/ready", "/api/emergency/analyze"}
    if path in public:
        return
    actor = await current_actor(request, db)
    if actor is None:
        return  # Local demo is a shared workspace, never a production auth policy.
    if path.startswith("/api/admin") and actor.role != "ADMIN":
        raise HTTPException(403, "Admin role required")
    ids = []
    if "scan_id" in request.path_params:
        ids.append(request.path_params["scan_id"])
    if path in {"/api/ai/investigate", "/api/compare"} and request.method == "POST":
        body = await request.json()
        if not isinstance(body, dict):
            raise HTTPException(422, "Expected a JSON object")
        ids.extend(body.get(k) for k in ("scan_id", "scan_id_a", "scan_id_b") if body.get(k))
    report_id = request.path_params.get("report_id")
    if report_id:
        report = db.query(SavedReport).filter((SavedReport.id == report_id) | (SavedReport.share_token == report_id)
                                            | (SavedReport.scan_id == report_id)).first()
        ids.append(report.scan_id if report else report_id)
    for scan_id in ids:
        scan = db.get(Scan, scan_id)
        if not scan or (actor.role != "ADMIN" and scan.user_id != actor.id):
            raise HTTPException(404, "Scan not found")
