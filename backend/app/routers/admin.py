from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth.dependencies import require_admin
from app.auth.security import hash_password
from app.services.signserver_connector import SignServerConnector
from app.services.ldap_connector import LDAPConnector

router=APIRouter(prefix='/api/admin', tags=['admin'])
@router.get('/users')
def users(db:Session=Depends(get_db), a=Depends(require_admin)): return db.query(User).all()
@router.post('/users')
def create_user(username:str=Form(...), email:str=Form(...), display_name:str=Form(...), role:str=Form(...), password:str=Form(...), db:Session=Depends(get_db), a=Depends(require_admin)):
    if db.query(User).filter(User.username==username).first(): raise HTTPException(400,'exists')
    db.add(User(username=username,email=email,display_name=display_name,role=role,password_hash=hash_password(password))); db.commit(); return {"message":"created"}
@router.put('/users/{user_id}')
def update_user(user_id:int, role:str=Form(...), is_active:bool=Form(...), db:Session=Depends(get_db), a=Depends(require_admin)):
    u=db.query(User).filter(User.id==user_id).first(); u.role=role; u.is_active=is_active; db.commit(); return {"message":"updated"}
@router.post('/users/{user_id}/reset-password')
def reset(user_id:int, password:str=Form(...), db:Session=Depends(get_db), a=Depends(require_admin)):
    u=db.query(User).filter(User.id==user_id).first(); u.password_hash=hash_password(password); u.must_change_password=True; db.commit(); return {"message":"reset"}
@router.get('/settings/signserver')
def ss(a=Depends(require_admin)): from app.config import settings; return {k:v for k,v in settings.model_dump().items() if k.startswith('signserver_') or k.startswith('tsa_')}
@router.post('/settings/signserver')
def ss_set(a=Depends(require_admin)): return {"message":"Use env vars for now"}
@router.get('/signserver/health')
def ss_h(a=Depends(require_admin)): return SignServerConnector().health_check()
@router.get('/settings/ldap')
def ldap_get(a=Depends(require_admin)): from app.config import settings; return {k:v for k,v in settings.model_dump().items() if k.startswith('ldap_')}
@router.post('/settings/ldap')
def ldap_set(a=Depends(require_admin)): return {"message":"Use env vars for now"}
@router.get('/ldap/test')
def ldap_test(a=Depends(require_admin)): return LDAPConnector().test_connection()
