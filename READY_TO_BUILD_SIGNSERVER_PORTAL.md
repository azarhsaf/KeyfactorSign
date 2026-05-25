# Keyfactor SignPortal - Technical Design & Limitations

This repository now includes a deployable full-stack application scaffold with:
- React + Vite + TypeScript + Tailwind frontend
- FastAPI backend with modular routers/services
- PostgreSQL models for users/documents/workflows/placements/audit/settings/jobs
- SignServer connector service (HTTP process servlet mode)
- LDAP connector placeholder service and test endpoint
- Nginx reverse proxy and Docker Compose deployment on port 8081

## Current limitations
- SignServer connector assumes process servlet style `/process?workerName=...`; adapt if your SignServer deployment uses a different endpoint.
- Timestamp verification is a backend placeholder (`timestamp_presence_placeholder`) until PDF signature validation module is added.
- LDAP test endpoint is intentionally a placeholder integration hook in this iteration.
- Frontend pages are production-style scaffolds; deeper forms/tables for every page can be iterated quickly on top of this structure.

## Next hardening tasks
1. Add Alembic migrations.
2. Replace placeholder LDAP test with real bind/search/group mapping.
3. Add full PDF signature/timestamp verification report endpoint.
4. Add UI forms for SignServer and LDAP settings persistence using `settings` table.
5. Add end-to-end integration tests.
