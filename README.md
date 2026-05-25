# Keyfactor SignPortal

## Deploy
```bash
cp .env.example .env
docker compose up -d --build
```
App: `http://<server-ip>:8081`

## Default users
- admin / Admin@123
- signer1 / Signer@123
- signer2 / Signer@123

## Key fixes included
- Token/session applied to all API calls, including preview/download blob flows.
- Completed documents supports signed/original secure downloads.
- SignServer settings + health + test-sign endpoints.
- LDAP settings/test/test-login/search/sync endpoints and Users & Directory page updates.
- SMTP/Email Relay settings + test connection + send-test email endpoint and UI page.

## Important env values
- `SIGNSERVER_BASE_URL` accepts either `.../signserver` or `.../signserver/process`.
- `SIGNSERVER_WORKER_ID=PDFSigner`
- `LDAP_*` values for AD/LDAP integration
- `SMTP_*` + `APP_PUBLIC_URL` for email notifications

## Troubleshooting
- If preview/download shows auth issue, re-login and verify token exists in browser storage.
- If SignServer sign fails, check `/api/admin/signserver/health` and `/api/admin/signserver/test-sign`.
- If LDAP test fails, verify bind DN/password and base DN.
- If SMTP test fails, verify host/port/TLS and credentials.
