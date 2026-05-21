# 1. Architecture Overview

A practical **lab-first architecture** is:

- **Frontend (React + Vite + Nginx)**: browser UI for login, upload, viewer, signature placement, workflow, admin.
- **Backend API (FastAPI)**: auth, RBAC, document orchestration, SignServer connector, audit.
- **PostgreSQL**: users, documents, workflow, settings, audit logs.
- **Object/File storage (local volume in Phase 1)**: original and signed PDFs.
- **SignServer (external in your lab)**: PDF signing + timestamping.
- **EJBCA (external in your lab)**: already integrated in Phase 1; Phase 2 for per-user cert issuance.
- **Optional LDAP/AD**: login and role mapping.

Recommended runtime in lab:

`Browser -> Nginx (frontend+reverse proxy) -> FastAPI -> PostgreSQL`

`FastAPI -> SignServer` and optionally `FastAPI -> LDAP`.

---

# 2. Recommended Technology Stack

## Chosen stack (simple + extensible)

- **Frontend**: React + TypeScript + Vite + Material UI
- **Backend**: Python **FastAPI** + SQLAlchemy + Alembic
- **DB**: PostgreSQL 16
- **Queue/async (optional later)**: Redis + Celery/RQ
- **Reverse proxy**: Nginx
- **Containerization**: Docker Compose
- **PDF viewer**: `react-pdf` (PDF.js)
- **Auth**: JWT (access + refresh), bcrypt password hashing

## Why this stack

- FastAPI gives quick API development and excellent OpenAPI docs.
- React gives polished, demo-friendly UI with reusable components.
- PostgreSQL is production-grade but still easy in Docker.
- Compose provides one-command lab deployment.
- Clean migration path to enterprise (K8s, SSO, HSM-backed keys).

---

# 3. Docker Compose Deployment Design

```yaml
version: "3.9"
services:
  db:
    image: postgres:16
    container_name: signportal-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: signportal
      POSTGRES_USER: signportal
      POSTGRES_PASSWORD: signportal_pass
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U signportal -d signportal"]
      interval: 10s
      timeout: 5s
      retries: 10

  backend:
    build: ./backend
    container_name: signportal-backend
    restart: unless-stopped
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./data/uploads:/app/data/uploads
      - ./data/signed:/app/data/signed
      - ./data/logs:/app/data/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 20s
      timeout: 5s
      retries: 5

  frontend:
    build: ./frontend
    container_name: signportal-frontend
    restart: unless-stopped
    depends_on:
      - backend

  nginx:
    image: nginx:1.27-alpine
    container_name: signportal-nginx
    restart: unless-stopped
    ports:
      - "8080:80"
      - "8443:443"
    volumes:
      - ./deploy/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./deploy/nginx/certs:/etc/nginx/certs:ro
    depends_on:
      - frontend
      - backend

volumes:
  pgdata:
```

### URL model
- `http://<host>:8080` -> portal UI.
- `/api/*` proxied to FastAPI.

---

# 4. Database Schema

## users
- id (PK)
- username (unique)
- email (unique)
- display_name
- role (`admin|uploader|signer|viewer`)
- password_hash
- ldap_user_flag (bool)
- is_active (bool)
- created_at

## documents
- id (PK)
- document_name
- description
- original_file_path
- signed_file_path (nullable)
- uploaded_by (FK users.id)
- status
- created_at
- updated_at

## workflows
- id (PK)
- document_id (FK documents.id)
- workflow_type (`single|sequential`)
- current_step (int)
- status
- created_at
- updated_at

## workflow_signers
- id (PK)
- workflow_id (FK workflows.id)
- signer_user_id (FK users.id)
- signing_order (int)
- status (`pending|signed|rejected`)
- signed_at
- signature_page
- signature_x
- signature_y
- signature_width
- signature_height
- signature_text

## audit_logs
- id (PK)
- document_id (nullable FK documents.id)
- user_id (nullable FK users.id)
- action
- details (jsonb)
- ip_address
- created_at

## app_settings
- id (PK, singleton row recommended)
- signserver_base_url
- signserver_worker_id
- signserver_auth_type
- signserver_username
- signserver_password_encrypted
- signserver_tls_verify
- tsa_url
- ldap_enabled
- ldap_host
- ldap_port
- ldap_bind_dn
- ldap_bind_password_encrypted
- ldap_base_dn
- ldap_group_admin
- ldap_group_signer
- updated_at

---

# 5. SignServer Connector Design

## Recommended interface
For modern web apps, prefer **SignServer HTTP Process servlet / REST-style HTTP endpoint** wrapped in a reusable backend connector.

Why:
- easiest to call from backend services
- simple payload handling for PDF bytes
- clear timeout/retry handling
- no CLI dependency inside containers

## Python connector shape

```python
class SignServerClient:
    def __init__(self, base_url, worker_id, auth_type="none", username=None, password=None,
                 tls_verify=True, timeout_seconds=60): ...

    def health_check(self) -> dict: ...
    def sign_pdf(self, pdf_bytes: bytes, metadata: dict) -> bytes: ...
```

## Behaviors required
- worker by ID/name
- auth modes: none/basic/bearer/mTLS
- strict timeout + retry (e.g., 2 retries with backoff)
- parse SignServer error responses into normalized API errors
- structured logging with request IDs

---

# 6. Timestamping Design

Timestamping is mandatory; use this priority:

1. **Option A (best for POC):** PDF signer worker applies timestamp directly.
2. **Option B:** dedicated TSA worker in SignServer referenced by signer worker.
3. **Option C:** external TSA URL configured in worker properties.

## Verification steps
After signing:
- open signed PDF in Adobe Reader / DSS / PDF validator
- confirm signature panel shows **trusted timestamp token**
- optionally run server-side check with a PDF signature library and log result

Backend should expose:
- `GET /api/documents/{id}/verify` -> signature_valid, timestamp_present, signer_subject

---

# 7. LDAP Integration Design

## Phase 1 (default)
- local DB auth only.

## Phase 2 LDAP/AD
- configurable from Admin settings.
- bind user with service account, search user, then authenticate user bind.
- map LDAP groups -> app roles.

Example mapping:
- `CN=SignPortalAdmins,...` -> admin
- `CN=SignPortalSigners,...` -> signer
- `CN=SignPortalViewers,...` -> viewer

Fallback strategy:
- if LDAP unavailable and user is local admin, allow emergency local login (optional feature flag).

---

# 8. Frontend Screens and UI Flow

1. **Login page**
   - username/password, optional LDAP toggle label.
2. **Dashboard**
   - cards: pending my signature, uploaded by me, completed, failed.
   - recent activity + workflow list table.
3. **Upload page**
   - drag/drop PDF, metadata, workflow type selector, signer selection.
4. **Document preview**
   - embedded PDF viewer with zoom/page navigation.
5. **Signature placement**
   - phase 1: coordinates form + visual helper overlay.
   - phase 1.5: drag-resize rectangle.
6. **Signing queue page**
   - actions for current signer only.
7. **Workflow tracking**
   - ordered signer steps with status badges.
8. **Completed docs**
   - download signed file + audit trail link.
9. **Admin settings**
   - SignServer/TSA/LDAP config and health checks.
10. **Audit log viewer**
    - filter by user/doc/date/action.

---

# 9. Single Signer Workflow

1. Uploader logs in.
2. Uploads PDF.
3. Sets signature coordinates/text.
4. Chooses single signer (self or another).
5. Signer clicks **Sign**.
6. Backend calls SignServer connector with worker + metadata.
7. SignServer returns signed PDF with timestamp.
8. Backend stores signed file, updates status to `Completed`.
9. Audit events persisted at every step.

---

# 10. Sequential Multi-Signer Workflow

1. Uploader uploads PDF and selects signers in order.
2. Create workflow rows with `signing_order`.
3. `current_step=1`; only signer 1 can sign.
4. After signer 1 signs, signed output becomes next input.
5. Increment `current_step`; unlock signer 2.
6. Repeat until final signer signs.
7. Mark document/workflow `Completed`.
8. Full audit chain includes every sign action and file hash.

Implementation note:
- keep each intermediate signed revision (optional but useful for demo and forensic checks).

---

# 11. Backend API Design

## Auth
- `POST /api/login`
- `POST /api/logout`
- `GET /api/me`
- `POST /api/token/refresh`

## Documents
- `POST /api/documents/upload`
- `GET /api/documents`
- `GET /api/documents/{id}`
- `GET /api/documents/{id}/download`
- `GET /api/documents/{id}/preview`

## Signature placement
- `POST /api/documents/{id}/signature-placement`
- `GET /api/documents/{id}/signature-placement`

## Signing
- `POST /api/documents/{id}/sign` (single signer)
- `POST /api/workflows/{id}/sign` (sequential step)

## Workflow
- `POST /api/workflows`
- `GET /api/workflows/{id}`
- `GET /api/workflows/{id}/history`

## Audit
- `GET /api/audit/{document_id}`
- `GET /api/audit` (filters)

## Admin
- `GET /api/admin/settings`
- `POST /api/admin/settings`
- `GET /api/health/signserver`
- `GET /api/health/ldap`
- `GET /api/health`

---

# 12. Sample Environment Configuration

```env
APP_NAME=SignPortal
APP_ENV=lab
APP_DEBUG=false
APP_SECRET_KEY=change_me
JWT_EXPIRE_MINUTES=60
JWT_REFRESH_EXPIRE_MINUTES=10080

DB_HOST=db
DB_PORT=5432
DB_NAME=signportal
DB_USER=signportal
DB_PASSWORD=signportal_pass

UPLOAD_DIR=/app/data/uploads
SIGNED_DIR=/app/data/signed
MAX_FILE_MB=25
ALLOWED_EXTENSIONS=pdf

SIGNSERVER_BASE_URL=https://signserver.lab.local:8443/signserver
SIGNSERVER_WORKER_ID=PDFSigner
SIGNSERVER_AUTH_TYPE=none
SIGNSERVER_USERNAME=
SIGNSERVER_PASSWORD=
SIGNSERVER_TLS_VERIFY=false
SIGNSERVER_TIMEOUT_SECONDS=60

TSA_URL=https://signserver.lab.local:8443/signserver/tsa

LDAP_ENABLED=false
LDAP_HOST=ad.lab.local
LDAP_PORT=636
LDAP_USE_SSL=true
LDAP_BIND_DN=CN=svc-signportal,OU=Service Accounts,DC=lab,DC=local
LDAP_BIND_PASSWORD=
LDAP_BASE_DN=DC=lab,DC=local
LDAP_USER_FILTER=(sAMAccountName={username})
LDAP_GROUP_ADMIN=CN=SignPortalAdmins,OU=Groups,DC=lab,DC=local
LDAP_GROUP_SIGNER=CN=SignPortalSigners,OU=Groups,DC=lab,DC=local
LDAP_GROUP_VIEWER=CN=SignPortalViewers,OU=Groups,DC=lab,DC=local
```

---

# 13. SignServer Worker Configuration Required

For Phase 1 PDF signing worker:

- Worker type: PDF signer.
- Crypto token configured with existing org certificate.
- Visible signature enabled (text template).
- Timestamping enabled (internal TSA worker or external TSA).
- Digest/signature algorithm aligned with policy (e.g., SHA-256 + RSA/ECDSA).

Example visible text template:
- `Digitally signed by: ${requestMetadata.username}`
- `Workflow step: ${requestMetadata.workflow_step}`
- `Date: ${requestMetadata.timestamp}`
- `Reason: Document Approval`

Also configure:
- max upload size
- accepted MIME type (application/pdf)
- auth requirement matching your connector

---

# 14. EJBCA Configuration Required

## Phase 1
- no new issuance required.
- ensure existing signer cert chain is valid and trusted by PDF validators.

## Phase 2 readiness
- define end entity profile per signer type.
- define certificate profile for document signing certs.
- prepare RA API credentials with least privilege.
- decide key strategy:
  - centrally generated keys (easier ops, higher key custody risk), or
  - remote/client-side signing (better non-repudiation, more complexity).

---

# 15. Full Step-by-Step Deployment Guide

1. Clone package and enter project directory.
2. Copy sample env:
   - `cp .env.example .env`
3. Edit `.env` for SignServer endpoint/worker and secrets.
4. Create TLS certs for Nginx (or run HTTP only in lab).
5. Build and start:
   - `docker compose up -d --build`
6. Run DB migrations:
   - `docker compose exec backend alembic upgrade head`
7. Seed admin/signer users:
   - `docker compose exec backend python scripts/seed.py`
8. Open portal:
   - `http://<host>:8080`
9. Login as admin, verify SignServer health in Admin Settings.
10. Upload a PDF and execute single signer flow.
11. Create sequential flow (2–3 signers) and validate progression.

---

# 16. Testing Procedure

## Functional
- login success/failure
- RBAC access boundaries
- upload PDF validation
- signature placement save/load
- single signer end-to-end sign
- sequential signer routing order
- download signed output
- audit trail completeness

## Integration
- SignServer health endpoint
- SignServer timeout/error simulation
- timestamp presence verification

## Non-functional
- max file size rejection
- unsupported file rejection
- concurrent signing attempts on same step

---

# 17. Troubleshooting

- **Cannot sign / 5xx from backend**: verify `SIGNSERVER_BASE_URL`, worker ID, TLS verify flag.
- **401/403 from SignServer**: validate auth mode and credentials.
- **Timestamp missing**: check signer worker timestamp config and TSA reachability.
- **Sequential flow stuck**: verify `current_step` and signer status transaction commit.
- **PDF not rendering in UI**: check CORS/`Content-Type` and PDF.js worker config.
- **LDAP login fails**: test bind DN credentials and search base/filter.

---

# 18. Future Enhancement: Per-user Certificates and LTV

## Per-user certificates
- On signer onboarding/login, map identity -> EJBCA profile.
- Request cert issuance through EJBCA RA API.
- Bind workflow step to signer certificate identity.
- Ensure each signature uses signer-specific credential.

## Risks and recommendations
- Central key generation simplifies UX but weakens non-repudiation.
- Enterprise approach: remote signing/HSM-backed keys with strong auth (MFA).
- Add OCSP/CRL evidence capture and archival.

## LTV roadmap
- embed revocation info at signing time when possible
- periodic archive timestamp renewal
- add verification endpoint and report export

---

# 19. Security Considerations

- bcrypt/argon2 password hashing.
- short-lived JWT + refresh token rotation.
- strict RBAC middleware.
- file validation by MIME + extension + magic bytes.
- storage path isolation; no direct filesystem exposure.
- signed download authorization checks.
- audit every sensitive action with IP and actor.
- secrets only via env/secret manager.
- TLS everywhere; optional mTLS to SignServer.
- rate limiting on login/sign endpoints.
- input validation with Pydantic schemas.

---

# 20. Complete Ready-to-Build Code Skeleton

```text
signportal/
  docker-compose.yml
  .env.example
  README.md
  deploy/
    nginx/
      nginx.conf
      certs/
  backend/
    Dockerfile
    requirements.txt
    alembic.ini
    alembic/
      versions/
    app/
      main.py
      core/
        config.py
        security.py
        rbac.py
        logging.py
      db/
        base.py
        session.py
        models/
          user.py
          document.py
          workflow.py
          audit.py
          settings.py
      schemas/
        auth.py
        user.py
        document.py
        workflow.py
        settings.py
      api/
        deps.py
        routes/
          auth.py
          users.py
          documents.py
          workflows.py
          audit.py
          admin.py
          health.py
      services/
        signserver_client.py
        workflow_service.py
        pdf_service.py
        ldap_service.py
        audit_service.py
      utils/
        file_store.py
        validators.py
    scripts/
      seed.py
  frontend/
    Dockerfile
    package.json
    vite.config.ts
    src/
      main.tsx
      App.tsx
      api/
        client.ts
        auth.ts
        documents.ts
        workflows.ts
        admin.ts
      pages/
        LoginPage.tsx
        DashboardPage.tsx
        UploadPage.tsx
        DocumentPreviewPage.tsx
        SignaturePlacementPage.tsx
        SigningQueuePage.tsx
        WorkflowTrackingPage.tsx
        CompletedDocsPage.tsx
        AdminSettingsPage.tsx
        AuditLogPage.tsx
      components/
        layout/SideNav.tsx
        dashboard/StatusCards.tsx
        documents/DocumentsTable.tsx
        pdf/PdfViewer.tsx
        pdf/SignatureOverlay.tsx
        common/StatusBadge.tsx
        common/ProtectedRoute.tsx
      store/
        authStore.ts
      styles/
        theme.ts
```

## Minimal implementation milestones
- **M1**: Auth + RBAC + upload + dashboard.
- **M2**: PDF preview + coordinate placement + single signer flow.
- **M3**: sequential workflow + audit UI.
- **M4**: admin settings + SignServer/LDAP health checks.
- **M5**: hardening + docs + demo data.

