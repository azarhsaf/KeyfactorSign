import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine, SessionLocal
from app.routers import auth, dashboard, documents, workflows, audit, admin
from app.services.seed_service import seed_defaults
import app.models

Base.metadata.create_all(bind=engine)
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.signed_dir, exist_ok=True)
seed_defaults(SessionLocal())

app = FastAPI(title="Keyfactor SignPortal API")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(',')], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get('/api/health')
def health():
    return {"status":"ok","app":"Keyfactor SignPortal"}

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(documents.router)
app.include_router(workflows.router)
app.include_router(audit.router)
app.include_router(admin.router)
