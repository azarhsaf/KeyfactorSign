from sqlalchemy.orm import Session
from app.models import AuditLog

def add_audit(db: Session, action: str, user_id=None, document_id=None, details="", status="info", ip=None, ua=None):
    db.add(AuditLog(action=action, user_id=user_id, document_id=document_id, details=details, status=status, ip_address=ip, user_agent=ua))
    db.commit()
