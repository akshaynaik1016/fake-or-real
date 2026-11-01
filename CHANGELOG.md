# Upgrade change log

The existing scanners, weighted score, deterministic investigator, emergency module,
PDFs, passports, extension source and application structure are preserved. The
upgrade adds an LLM-optional evidence workflow, provenance, bounded research,
correlation-aware fusion, interactive graph and executable next checks. It fixes
fabricated evidence/fallbacks and key configuration/auth issues. Original tests were
not changed or deleted; 56 additional parametrized cases bring the total to 84.

Generated build files, installed dependencies and verification logs are excluded
from this source list. The original databases are byte-for-byte unchanged.

| Change | File |
|---|---|
| Modified | `.env.example` |
| Modified | `AI.md` |
| Modified | `API.md` |
| Modified | `ARCHITECTURE.md` |
| Added | `BUILD_STATUS.md` |
| Added | `CODEBASE_AUDIT.md` |
| Modified | `DATABASE.md` |
| Modified | `DEMO.md` |
| Modified | `DEPLOYMENT.md` |
| Added | `IMPLEMENTATION_PLAN.md` |
| Modified | `LIMITATIONS.md` |
| Modified | `PRIVACY.md` |
| Modified | `README.md` |
| Modified | `SECURITY.md` |
| Added | `backend/.dockerignore` |
| Added | `backend/alembic.ini` |
| Added | `backend/app/agents/investigation_orchestrator.py` |
| Modified | `backend/app/api/v1/api.py` |
| Modified | `backend/app/api/v1/endpoints/admin.py` |
| Modified | `backend/app/api/v1/endpoints/ai_chat.py` |
| Modified | `backend/app/api/v1/endpoints/analyze.py` |
| Modified | `backend/app/api/v1/endpoints/auth.py` |
| Modified | `backend/app/api/v1/endpoints/community.py` |
| Modified | `backend/app/api/v1/endpoints/compare.py` |
| Modified | `backend/app/api/v1/endpoints/dashboard.py` |
| Modified | `backend/app/api/v1/endpoints/demo.py` |
| Modified | `backend/app/api/v1/endpoints/health.py` |
| Added | `backend/app/api/v1/endpoints/investigations.py` |
| Modified | `backend/app/api/v1/endpoints/reports.py` |
| Modified | `backend/app/api/v1/endpoints/scans.py` |
| Modified | `backend/app/api/v1/endpoints/trust_passport.py` |
| Added | `backend/app/core/access.py` |
| Modified | `backend/app/core/config.py` |
| Added | `backend/app/integrations/llm/provider.py` |
| Modified | `backend/app/integrations/threat_intel/manager.py` |
| Modified | `backend/app/integrations/threat_intel/providers.py` |
| Added | `backend/app/integrations/web_research/tavily_service.py` |
| Modified | `backend/app/main.py` |
| Modified | `backend/app/models/all_models.py` |
| Modified | `backend/app/ocr/ocr_engine.py` |
| Modified | `backend/app/scanners/domain_scanner.py` |
| Modified | `backend/app/scanners/payment_scanner.py` |
| Modified | `backend/app/scanners/phone_scanner.py` |
| Modified | `backend/app/scanners/ssl_scanner.py` |
| Modified | `backend/app/scanners/text_scanner.py` |
| Modified | `backend/app/schemas/all_schemas.py` |
| Added | `backend/app/schemas/investigation.py` |
| Modified | `backend/app/security/file_validator.py` |
| Modified | `backend/app/security/redaction.py` |
| Modified | `backend/app/security/ssrf.py` |
| Modified | `backend/app/services/ai_investigator.py` |
| Added | `backend/app/services/bayesian_evidence_engine.py` |
| Modified | `backend/app/services/demo_seed.py` |
| Added | `backend/app/services/evidence_service.py` |
| Added | `backend/app/services/investigation_execution.py` |
| Added | `backend/app/services/investigation_store.py` |
| Added | `backend/app/services/next_best_investigation.py` |
| Modified | `backend/app/services/report_generator.py` |
| Modified | `backend/app/services/scan_service.py` |
| Added | `backend/app/services/trust_graph_service.py` |
| Added | `backend/migrations/env.py` |
| Added | `backend/migrations/versions/0001_investigation_snapshots.py` |
| Added | `backend/requirements-tested.txt` |
| Modified | `backend/requirements.txt` |
| Modified | `docker-compose.yml` |
| Added | `frontend/.dockerignore` |
| Modified | `frontend/Dockerfile` |
| Modified | `frontend/package-lock.json` |
| Modified | `frontend/package.json` |
| Modified | `frontend/src/api/client.ts` |
| Modified | `frontend/src/components/common/AIInvestigatorModal.tsx` |
| Modified | `frontend/src/components/common/EvidenceCard.tsx` |
| Added | `frontend/src/components/common/InvestigationPanel.tsx` |
| Added | `frontend/src/components/common/TrustGraph.tsx` |
| Modified | `frontend/src/components/common/TrustPassportModal.tsx` |
| Modified | `frontend/src/components/common/TrustScoreCircle.tsx` |
| Modified | `frontend/src/components/common/VerificationChecklist.tsx` |
| Modified | `frontend/src/components/layout/Footer.tsx` |
| Modified | `frontend/src/pages/AdminPage.tsx` |
| Modified | `frontend/src/pages/DashboardPage.tsx` |
| Modified | `frontend/src/pages/DemoPage.tsx` |
| Modified | `frontend/src/pages/HistoryPage.tsx` |
| Modified | `frontend/src/pages/LoginPage.tsx` |
| Modified | `frontend/src/pages/RegisterPage.tsx` |
| Modified | `frontend/src/pages/ScanResultPage.tsx` |
| Modified | `frontend/src/pages/TrustPassportPage.tsx` |
| Added | `tests/conftest.py` |
| Added | `tests/test_investigation.py` |
