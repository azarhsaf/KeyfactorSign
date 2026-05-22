# Keyfactor SignPortal

Professional POC portal for SignServer-backed PDF signing.

## Stack
React + Vite + TypeScript + Tailwind, FastAPI, PostgreSQL, Nginx, Docker Compose.

## Deploy
```bash
cp .env.example .env
docker compose up -d --build
```
Open `http://<server-ip>:8081`.

## Default users
- admin / Admin@123 (must change password)
- signer1 / Signer@123
- signer2 / Signer@123

## SignServer
Configure in `.env` using `SIGNSERVER_*`. Health check: `GET /api/admin/signserver/health`.

## TSA
Set `TSA_ENABLED`, `TSA_URL`, `TSA_WORKER_NAME`.

## LDAP
Set `LDAP_*` and test via `GET /api/admin/ldap/test`.

## Workflows
- Single signer: upload + one signer + sign.
- Sequential: multiple signers ordered; each signs when current step reaches them.

## Troubleshooting
- If login fails: verify DB initialized and seed users exist.
- If signing fails: verify SignServer endpoint and worker settings.
- If PDF preview fails: ensure uploaded file is valid PDF.
