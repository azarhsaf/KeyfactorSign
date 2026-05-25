from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AuditLog
from app.auth.dependencies import get_current_user

router=APIRouter(prefix='/api/audit', tags=['audit'])
@router.get('')
def get_all(db:Session=Depends(get_db), user=Depends(get_current_user)): return db.query(AuditLog).order_by(AuditLog.id.desc()).all()
@router.get('/{document_id}')
def get_doc(document_id:int, db:Session=Depends(get_db), user=Depends(get_current_user)): return db.query(AuditLog).filter(AuditLog.document_id==document_id).all()
