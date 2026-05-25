from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document, WorkflowSigner, SigningJob
from app.models.settings import EmailLog
from app.models.audit import AuditLog
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get('/summary')
def summary(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return {
        "total_documents": db.query(Document).count(),
        "pending_my_signature": db.query(WorkflowSigner).filter(WorkflowSigner.signer_user_id==user.id, WorkflowSigner.status=='pending').count(),
        "uploaded_by_me": db.query(Document).filter(Document.uploaded_by==user.id).count(),
        "completed_documents": db.query(Document).filter(Document.status=='Completed').count(),
        "failed_signing_jobs": db.query(SigningJob).filter(SigningJob.status=='failed').count(),
        "failed_documents": db.query(Document).filter(Document.status=='Failed').count(),
        "emails_sent": db.query(EmailLog).filter(EmailLog.status=='sent').count(),
        "emails_failed": db.query(EmailLog).filter(EmailLog.status=='failed').count(),
        "recent_activity": [
            {"action": a.action, "status": a.status, "document_id": a.document_id, "created_at": a.created_at.isoformat() if a.created_at else None}
            for a in db.query(AuditLog).order_by(AuditLog.id.desc()).limit(10).all()
        ],
        "pending_documents": [d.id for d in db.query(Document).filter(Document.status.in_(['Pending Signature','In Progress'])).limit(10).all()],
        "completed_documents_list": [d.id for d in db.query(Document).filter(Document.status=='Completed').order_by(Document.id.desc()).limit(10).all()],
    }
