import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging_config import audit_logger
from app.api.v1.api import api_router
from app.core.rate_limiter import rate_limiter

# Ensure all database tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Evidence-Based Digital Trust & Safety Platform. Don't trust. Verify.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers & Audit Logging Middleware
@app.middleware("http")
async def security_headers_and_logging_middleware(request: Request, call_next):
    start_time = time.time()
    if request.method == "POST":
        allowed, _ = rate_limiter.is_allowed(request.client.host if request.client else "unknown", limit=60)
        if not allowed:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"}, headers={"Retry-After": "60"})
    
    # Process request
    response = await call_next(request)
    
    duration_ms = round((time.time() - start_time) * 1000, 2)
    
    # Inject Security Headers (Requirement 57)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data: https:; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self' http://localhost:* http://127.0.0.1:* ws:;"
    )
    
    # Log structured event
    audit_logger.log_event(
        operation=f"{request.method} {request.url.path}",
        status=str(response.status_code),
        duration_ms=duration_ms
    )
    
    return response

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root_endpoint():
    return {
        "platform": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "api_docs": "/docs",
        "demo_mode": settings.DEMO_MODE,
        "status": "OPERATIONAL"
    }
