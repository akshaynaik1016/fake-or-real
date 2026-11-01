from fastapi import APIRouter, Depends
from app.core.access import enforce_access
from app.api.v1.endpoints import (
    auth,
    analyze,
    scans,
    reports,
    community,
    dashboard,
    emergency,
    trust_passport,
    compare,
    ai_chat,
    admin,
    demo,
    health,
    investigations,
    cases
)

api_router = APIRouter(dependencies=[Depends(enforce_access)])

api_router.include_router(auth.router)
api_router.include_router(analyze.router)
api_router.include_router(scans.router)
api_router.include_router(reports.router)
api_router.include_router(community.router)
api_router.include_router(dashboard.router)
api_router.include_router(emergency.router)
api_router.include_router(trust_passport.router)
api_router.include_router(compare.router)
api_router.include_router(ai_chat.router)
api_router.include_router(admin.router)
api_router.include_router(demo.router)
api_router.include_router(health.router)

api_router.include_router(investigations.router)

api_router.include_router(cases.router)
