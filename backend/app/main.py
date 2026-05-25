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

from app.services.settings_service import get_category
from app.database import SessionLocal

@app.get('/api/branding')
def public_branding():
    db = SessionLocal()
    try:
        cfg = {
            "brand_product_name": settings.brand_product_name,
            "brand_company_name": settings.brand_company_name,
            "brand_logo_path": settings.brand_logo_path,
            "brand_primary_color": settings.brand_primary_color,
            "brand_secondary_color": settings.brand_secondary_color,
            "brand_login_background_text": settings.brand_login_background_text,
            "brand_footer_text": settings.brand_footer_text,
        }
        cfg.update(get_category(db, 'branding'))
        return cfg
    finally:
        db.close()
