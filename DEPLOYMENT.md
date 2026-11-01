# Deployment

For a local loopback demo, follow README.md. No model process is required.

For a public environment, set ENVIRONMENT=production, DEMO_MODE=false, a unique
JWT_SECRET of at least 32 characters and explicit BACKEND_CORS_ORIGINS. Configure
a database, HTTPS reverse proxy, backups, parser isolation and distributed controls.
Review SECURITY.md and LIMITATIONS.md before deployment; no production certification
is claimed. Bootstrap an administrator through trusted database administration,
not through an unauthenticated HTTP route.

Docker Compose source is retained and updated to require JWT_SECRET and
POSTGRES_PASSWORD instead of hardcoded secrets. It uses PostgreSQL via psycopg,
Redis and the existing Nginx SPA/API proxy. The frontend build uses /api, and the
backend remains provider independent with AI_PROVIDER=none by default. Run migrations
before serving an existing database. Set BACKEND_CORS_ORIGINS to the actual frontend
origin. Docker and PostgreSQL were not run in this environment; only the local
SQLite/API/frontend workflow was tested.

Set VITE_API_BASE in frontend/.env.local for a separate frontend/backend origin;
never put service credentials in VITE_ variables. Optional Tavily and Google Safe
Browsing keys belong only in backend configuration. Provider-specific local/hosted
LLM deployment is intentionally deferred and is not a startup prerequisite.
