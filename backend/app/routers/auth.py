from datetime import datetime
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth.security import verify_password, create_access_token, hash_password
from app.auth.dependencies import get_current_user
from app.config import settings
from app.services.ldap_connector import LDAPConnector
from app.services.audit_service import add_audit

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post('/login')
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username, User.is_active == True).first()

    # Local-first admin fallback when LDAP is enabled but unavailable.
    if user and verify_password(password, user.password_hash):
        user.last_login_at = datetime.utcnow(); db.commit()
        add_audit(db, 'LOGIN_SUCCESS_LOCAL', user.id)
        return {"access_token": create_access_token({"sub": user.username, "role": user.role}), "token_type": "bearer", "must_change_password": user.must_change_password}

    if settings.ldap_enabled:
        try:
            li = LDAPConnector().authenticate(username, password)
            if li:
                if not user:
                    user = User(username=li['username'], email=li['email'], display_name=li['display_name'], role=li['role'], password_hash=hash_password(password), auth_source='ldap', must_change_password=False)
                    db.add(user)
                else:
                    user.email = li['email']; user.display_name = li['display_name']; user.role = li['role']; user.auth_source = 'ldap'
                user.last_login_at = datetime.utcnow(); db.commit(); db.refresh(user)
                add_audit(db, 'LOGIN_SUCCESS_LDAP', user.id)
                return {"access_token": create_access_token({"sub": user.username, "role": user.role}), "token_type": "bearer", "must_change_password": user.must_change_password}
        except Exception as ex:
            # fallback to local-only failure handling
            if user and verify_password(password, user.password_hash):
                user.last_login_at = datetime.utcnow(); db.commit()
                return {"access_token": create_access_token({"sub": user.username, "role": user.role}), "token_type": "bearer", "must_change_password": user.must_change_password}
            raise HTTPException(status_code=401, detail=f"LDAP authentication failed: {ex}")

    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post('/change-password')
def change_password(new_password: str = Form(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    db.commit()
    add_audit(db, 'CHANGE_PASSWORD', user.id)
    return {"message": "Password changed"}

@router.get('/me')
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "role": user.role, "must_change_password": user.must_change_password}
