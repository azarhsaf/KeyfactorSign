from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document, WorkflowSigner, SigningJob
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get('/summary')
def summary(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return {
        "pending_my_signature": db.query(WorkflowSigner).filter(WorkflowSigner.signer_user_id==user.id, WorkflowSigner.status=='pending').count(),
        "uploaded_by_me": db.query(Document).filter(Document.uploaded_by==user.id).count(),
        "completed_documents": db.query(Document).filter(Document.status=='Completed').count(),
        "failed_signing_jobs": db.query(SigningJob).filter(SigningJob.status=='failed').count(),
        "total_documents": db.query(Document).count(),
    }
