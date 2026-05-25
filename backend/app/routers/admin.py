from fastapi import APIRouter, Depends, Form, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth.dependencies import require_admin
from app.auth.security import hash_password
from app.services.signserver_connector import SignServerConnector
from app.services.ldap_connector import LDAPConnector
from app.services.email_service import EmailService

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

@router.post('/users/{user_id}/reset-password')
def reset(user_id: int, password: str = Form(...), db: Session = Depends(get_db), a=Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u: raise HTTPException(404, 'not found')
    u.password_hash = hash_password(password); u.must_change_password = True; db.commit(); return {"message": "reset"}

@router.get('/signserver/settings')
def signserver_settings(a=Depends(require_admin)):
    from app.config import settings
    return {k: v for k, v in settings.model_dump().items() if k.startswith('signserver_') or k.startswith('tsa_')}

@router.post('/signserver/settings')
def signserver_settings_save(a=Depends(require_admin)):
    return {"message": "env-driven in current build"}

@router.get('/signserver/health')
def ss_h(a=Depends(require_admin)):
    return SignServerConnector().health_check()

@router.get('/signserver/test-sign')
def ss_test_sign(a=Depends(require_admin)):
    return SignServerConnector().test_signing()

@router.get('/ldap/settings')
def ldap_get(a=Depends(require_admin)):
    from app.config import settings
    return {k: v for k, v in settings.model_dump().items() if k.startswith('ldap_')}

@router.post('/ldap/settings')
def ldap_save(a=Depends(require_admin)):
    return {"message": "env-driven in current build"}

@router.get('/ldap/test')
def ldap_test(a=Depends(require_admin)):
    return LDAPConnector().test_connection()

@router.post('/ldap/test-login')
def ldap_test_login(username: str = Form(...), password: str = Form(...), a=Depends(require_admin)):
    data = LDAPConnector().authenticate(username, password)
    return {"ok": bool(data), "user": data}

@router.get('/ldap/search-users')
def ldap_search_users(q: str = Query(''), db: Session = Depends(get_db), a=Depends(require_admin)):
    rows = db.query(User).filter(User.auth_source == 'ldap').all()
    if q:
        rows = [r for r in rows if q.lower() in r.username.lower() or q.lower() in r.display_name.lower()]
    return rows

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
def smtp_settings(a=Depends(require_admin)):
    return EmailService().settings_dict()

@router.post('/smtp/settings')
def smtp_settings_save(a=Depends(require_admin)):
    return {"message": "env-driven in current build"}

@router.post('/smtp/test')
def smtp_test(a=Depends(require_admin), db: Session = Depends(get_db)):
    cfg = EmailService().settings_dict()
    return {"ok": bool(cfg['smtp_host']), "config": cfg}

@router.post('/smtp/send-test')
def smtp_send_test(to_email: str = Form(...), a=Depends(require_admin), db: Session = Depends(get_db)):
    return EmailService().send(db, to_email, 'Keyfactor SignPortal SMTP Test', '<b>SMTP test successful</b>')
