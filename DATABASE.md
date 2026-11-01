# Database compatibility

Existing SQLAlchemy tables are retained, including users, scans, scan_evidence,
verification_results, reports and community records. No existing columns are changed.
The archive contains databases at project root and backend/; relative SQLite paths
are based on the working directory. Run from backend/ or set an absolute URL.

Back up an existing database, then from backend/ run:

```sh
alembic upgrade head
```

Revision `0001_investigations` adds `investigation_states` (one versioned JSON snapshot
per scan) and `investigation_executions` (follow-up before/after records). It also
works if startup already created the tables. The JSON aggregate holds evidence,
sources, relationships, recommendations and calculations without duplicating them
across many new tables. Original scan IDs, evidence rows and history are retained.
Fresh startup preserves the existing create_all convention for local development.

Reads of old scans backfill from retained observations only and mark unknown
provenance/coverage. No automatic reanalysis or remote provider call occurs.
New scans save their canonical evidence IDs in the snapshot and legacy evidence
rows separately, since old primary keys are globally unique per row.

SQLite migration preservation/idempotence is tested, including on a copy of the
provided backend database. PostgreSQL uses the SQLAlchemy psycopg driver; its
migration/deployment path has not been exercised. Downgrade explicitly drops only
the two new tables and loses their data; it should not be used without a backup.
