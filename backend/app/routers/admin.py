import os
from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth.dependencies import require_admin
from app.auth.security import hash_password
from app.services.signserver_connector import SignServerConnector
from app.services.ldap_connector import LDAPConnector
from app.services.email_service import EmailService
from app.services.settings_service import get_category, set_setting, masked_payload
from app.services.runtime_config_service import effective_ldap_config, effective_smtp_config
from app.config import settings

router = APIRouter(prefix='/api/admin', tags=['admin'])

@router.get('/users')
def users(db: Session = Depends(get_db), a=Depends(require_admin)):
    return db.query(User).order_by(User.id).all()

@router.post('/users')
def create_user(username: str = Form(...), email: str = Form(...), display_name: str = Form(...), role: str = Form(...), password: str = Form(...), db: Session = Depends(get_db), a=Depends(require_admin)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(400, 'exists')
    db.add(User(username=username, email=email, display_name=display_name, role=role, password_hash=hash_password(password), auth_source='local'))
    db.commit(); return {"message": "created"}

@router.put('/users/{user_id}')
def update_user(user_id: int, role: str = Form(...), is_active: bool = Form(...), db: Session = Depends(get_db), a=Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u: raise HTTPException(404, 'not found')
    u.role = role; u.is_active = is_active; db.commit(); return {"message": "updated"}

@router.post('/users/{user_id}/disable')
def disable_user(user_id: int, db: Session = Depends(get_db), a=Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u: raise HTTPException(404, 'not found')
    u.is_active = False; db.commit(); return {"message": "disabled"}

@router.post('/users/{user_id}/enable')
def enable_user(user_id: int, db: Session = Depends(get_db), a=Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u: raise HTTPException(404, 'not found')
    u.is_active = True; db.commit(); return {"message": "enabled"}

@router.post('/users/{user_id}/reset-password')
def reset(user_id: int, password: str = Form(...), db: Session = Depends(get_db), a=Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u: raise HTTPException(404, 'not found')
    u.password_hash = hash_password(password); u.must_change_password = True; db.commit(); return {"message": "reset"}

@router.get('/signserver/settings')
def signserver_settings(db: Session = Depends(get_db), a=Depends(require_admin)):
    cfg = {
        "signserver_base_url": settings.signserver_base_url,
        "signserver_worker_id": settings.signserver_worker_id,
        "signserver_auth_type": settings.signserver_auth_type,
        "signserver_username": settings.signserver_username,
        "signserver_password": settings.signserver_password,
        "signserver_tls_verify": settings.signserver_tls_verify,
        "signserver_client_cert": settings.signserver_client_cert,
        "signserver_client_key": settings.signserver_client_key,
        "signserver_timeout": settings.signserver_timeout,
        "signserver_mode": settings.signserver_mode,
        "tsa_enabled": settings.tsa_enabled,
        "tsa_url": settings.tsa_url,
        "tsa_worker_name": settings.tsa_worker_name,
    }
    cfg.update(get_category(db, 'signserver'))
    return masked_payload(cfg)

@router.post('/signserver/settings')
def signserver_settings_save(db: Session = Depends(get_db), a=Depends(require_admin), signserver_base_url: str = Form(None), signserver_worker_id: str = Form(None), signserver_auth_type: str = Form(None), signserver_username: str = Form(None), signserver_password: str = Form(None), signserver_tls_verify: str = Form(None), signserver_timeout: str = Form(None), signserver_mode: str = Form(None), tsa_enabled: str = Form(None), tsa_url: str = Form(None), tsa_worker_name: str = Form(None)):
    fields = locals().copy();
    for k in ['db','a']:
        fields.pop(k, None)
    for k,v in fields.items():
        if v is not None and v != '': set_setting(db,'signserver',k,v)
    return {"message": "saved"}

@router.get('/signserver/health')
def ss_h(a=Depends(require_admin)):
    return SignServerConnector().health_check()

@router.post('/signserver/test-signing')
def ss_test_sign(a=Depends(require_admin)):
    return SignServerConnector().test_signing()

@router.get('/ldap/settings')
def ldap_get(db: Session = Depends(get_db), a=Depends(require_admin)):
    return masked_payload(effective_ldap_config(db))

@router.post('/ldap/settings')
def ldap_save(db: Session = Depends(get_db), a=Depends(require_admin), ldap_enabled: str = Form(None), ldap_url: str = Form(None), ldap_bind_dn: str = Form(None), ldap_bind_password: str = Form(None), ldap_base_dn: str = Form(None), ldap_user_filter: str = Form(None), ldap_admin_group: str = Form(None), ldap_signer_group: str = Form(None), ldap_viewer_group: str = Form(None), ldap_tls_verify: str = Form(None)):
    fields = locals().copy();
    for k in ['db','a']:
        fields.pop(k, None)
    for k,v in fields.items():
        if v is not None and v != '': set_setting(db,'ldap',k,v)
    return {"message":"saved"}

@router.get('/ldap/test')
def ldap_test(a=Depends(require_admin)):
    return LDAPConnector(effective_ldap_config(db)).test_connection()

@router.post('/ldap/test-login')
def ldap_test_login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db), a=Depends(require_admin)):
    data = LDAPConnector(effective_ldap_config(db)).authenticate(username, password)
    return {"ok": bool(data), "user": data}

@router.get('/ldap/search-users')
def ldap_search_users(query: str = Query(''), db: Session = Depends(get_db), a=Depends(require_admin)):
    return LDAPConnector(effective_ldap_config(db)).search_users(query)

@router.post('/ldap/sync-user')
def ldap_sync_user(username: str = Form(...), role: str = Form('signer'), db: Session = Depends(get_db), a=Depends(require_admin)):
    u = db.query(User).filter(User.username == username).first()
    if not u:
        u = User(username=username, email=f'{username}@ldap.local', display_name=username, role=role, password_hash=hash_password('Temp#12345'), auth_source='ldap', must_change_password=False)
        db.add(u)
    else:
        u.role = role; u.auth_source = 'ldap'
    db.commit(); return {"message": "synced"}

@router.get('/smtp/settings')
def smtp_settings(db: Session = Depends(get_db), a=Depends(require_admin)):
    return masked_payload(effective_smtp_config(db))

@router.post('/smtp/settings')
def smtp_settings_save(db: Session = Depends(get_db), a=Depends(require_admin), smtp_enabled: str = Form(None), smtp_host: str = Form(None), smtp_port: str = Form(None), smtp_username: str = Form(None), smtp_password: str = Form(None), smtp_use_tls: str = Form(None), smtp_from_email: str = Form(None), smtp_from_name: str = Form(None), app_public_url: str = Form(None)):
    fields = locals().copy();
    for k in ['db','a']:
        fields.pop(k, None)
    for k,v in fields.items():
        if v is not None and v != '': set_setting(db,'smtp',k,v)
    return {"message":"saved"}

@router.post('/smtp/test')
def smtp_test(a=Depends(require_admin), db: Session = Depends(get_db)):
    cfg = effective_smtp_config(db)
    return {"ok": bool(cfg['smtp_host']), "config": masked_payload(cfg)}

@router.post('/smtp/send-test')
def smtp_send_test(to_email: str = Form(...), a=Depends(require_admin), db: Session = Depends(get_db)):
    return EmailService().send(db, to_email, 'Keyfactor SignPortal SMTP Test', '<b>SMTP test successful</b>')

@router.get('/branding')
def branding_get(db: Session = Depends(get_db), a=Depends(require_admin)):
    cfg = {
        "brand_product_name": settings.brand_product_name,
        "brand_company_name": settings.brand_company_name,
        "brand_logo_path": settings.brand_logo_path,
        "brand_favicon_path": settings.brand_favicon_path,
        "brand_primary_color": settings.brand_primary_color,
        "brand_secondary_color": settings.brand_secondary_color,
        "brand_login_background_text": settings.brand_login_background_text,
        "brand_footer_text": settings.brand_footer_text,
    }
    cfg.update(get_category(db,'branding'))
    return cfg

@router.post('/branding')
def branding_save(db: Session = Depends(get_db), a=Depends(require_admin), brand_product_name: str = Form(None), brand_company_name: str = Form(None), brand_primary_color: str = Form(None), brand_secondary_color: str = Form(None), brand_login_background_text: str = Form(None), brand_footer_text: str = Form(None)):
    fields = locals().copy()
    for k in ['db','a']:
        fields.pop(k,None)
    for k,v in fields.items():
        if v is not None and v != '': set_setting(db,'branding',k,v)
    return {"message":"saved"}

@router.post('/branding/logo')
def branding_logo(file: UploadFile = File(...), db: Session = Depends(get_db), a=Depends(require_admin)):
    os.makedirs('/app/storage/branding', exist_ok=True)
    path = f"/app/storage/branding/logo_{file.filename}"
    with open(path,'wb') as f: f.write(file.file.read())
    set_setting(db,'branding','brand_logo_path',path)
    return {"message":"uploaded", "path": path}

@router.post('/branding/favicon')
def branding_favicon(file: UploadFile = File(...), db: Session = Depends(get_db), a=Depends(require_admin)):
    os.makedirs('/app/storage/branding', exist_ok=True)
    path = f"/app/storage/branding/favicon_{file.filename}"
    with open(path,'wb') as f: f.write(file.file.read())
    set_setting(db,'branding','brand_favicon_path',path)
    return {"message":"uploaded", "path": path}

@router.get('/system/diagnostics')
def system_diag(db: Session = Depends(get_db), a=Depends(require_admin)):
    from app.services.signserver_connector import SignServerConnector
    from app.services.ldap_connector import LDAPConnector
    from app.services.email_service import EmailService
    return {
        "backend": "ok",
        "database": "ok",
        "signserver": SignServerConnector().health_check(),
        "ldap": LDAPConnector().test_connection(),
        "smtp": {"enabled": EmailService().settings_dict().get('smtp_enabled'), "host": EmailService().settings_dict().get('smtp_host')},
        "storage": {
            "upload_dir": os.path.isdir('/app/storage/uploads'),
            "signed_dir": os.path.isdir('/app/storage/signed'),
            "branding_dir": os.path.isdir('/app/storage/branding')
        }
    }
