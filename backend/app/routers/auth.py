from datetime import datetime
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth.security import verify_password, create_access_token, hash_password
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post('/login')
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user.last_login_at = datetime.utcnow(); db.commit()
    return {"access_token": create_access_token({"sub": user.username, "role": user.role}), "token_type": "bearer", "must_change_password": user.must_change_password}

@router.post('/change-password')
def change_password(new_password: str = Form(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    db.commit()
    return {"message": "Password changed"}

@router.get('/me')
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "role": user.role, "must_change_password": user.must_change_password}
