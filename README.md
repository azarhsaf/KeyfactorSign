# SignPortal (POC App)

A deployable demo web app for testing Keyfactor SignServer as a backend signing engine.

## Quick Start
1. Copy env: `cp .env.example .env`
2. Start: `docker compose up -d --build`
3. Open: `http://localhost:8080`

## Features implemented
- Local user register/login (JWT)
- PDF upload
- Single/sequential workflow setup
- Sequential step signing endpoint
- Audit log retrieval
- Basic portal UI

## Core APIs
- POST /api/register
- POST /api/login
- GET /api/me
- POST /api/documents/upload
- GET /api/documents
- POST /api/workflows/{id}/sign
- GET /api/audit/{document_id}

## Note
Current signing step simulates signing by copying PDF to signed folder. Integrate actual SignServer call in `backend/app/main.py` signing flow for production.
