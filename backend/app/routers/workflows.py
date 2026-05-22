from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Workflow, WorkflowSigner, Document, SigningJob
from app.auth.dependencies import get_current_user
from app.services.signserver_connector import SignServerConnector
from app.services.pdf_service import timestamp_presence_placeholder
from app.services.audit_service import add_audit

router = APIRouter(prefix='/api/workflows', tags=['workflows'])

@router.post('')
def create_workflow():
    return {"message": "Use /api/documents/upload"}

@router.get('/{workflow_id}')
def get_workflow(workflow_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(404, 'Workflow not found')
    signers = db.query(WorkflowSigner).filter(WorkflowSigner.workflow_id == workflow_id).order_by(WorkflowSigner.signing_order).all()
    return {
        "id": wf.id, "document_id": wf.document_id, "workflow_type": wf.workflow_type,
        "status": wf.status, "current_step": wf.current_step,
        "signers": [{"id": s.id, "signer_user_id": s.signer_user_id, "signing_order": s.signing_order, "status": s.status} for s in signers]
    }

@router.post('/{workflow_id}/sign')
def sign(workflow_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf: raise HTTPException(404, 'Workflow not found')
    step = db.query(WorkflowSigner).filter(WorkflowSigner.workflow_id == workflow_id, WorkflowSigner.signing_order == wf.current_step).first()
    if not step or step.signer_user_id != user.id:
        raise HTTPException(403, 'Not your step')
    doc = db.query(Document).filter(Document.id == wf.document_id).first()
    out = f"{doc.current_file_path.rsplit('.pdf',1)[0]}_step{wf.current_step}_signed.pdf"
    job = SigningJob(document_id=doc.id, workflow_signer_id=step.id, status='running')
    db.add(job); db.commit(); db.refresh(job)
    try:
        result = SignServerConnector().sign_pdf(doc.current_file_path, out, {"username": user.username, "doc_id": doc.id})
        step.status = 'signed'; step.signed_at = datetime.utcnow(); doc.current_file_path = out; doc.signed_file_path = out
        total = db.query(WorkflowSigner).filter(WorkflowSigner.workflow_id == workflow_id).count()
        if wf.current_step >= total:
            wf.status = 'Completed'; doc.status = 'Completed'
        else:
            wf.current_step += 1; wf.status = 'In Progress'; doc.status = 'In Progress'
        job.status = 'success'; job.signserver_request_id = str(result.get('status_code'))
        ts = timestamp_presence_placeholder(out)
        add_audit(db, 'SIGN_SUCCESS', user.id, doc.id, f'workflow={workflow_id}')
        db.commit()
        return {"status": wf.status, "timestamp": ts}
    except Exception as ex:
        job.status = 'failed'; job.error_message = str(ex); doc.status = 'Failed'; wf.status = 'Failed'
        add_audit(db, 'SIGN_FAILED', user.id, doc.id, str(ex))
        db.commit()
        raise HTTPException(502, f'SignServer signing failed: {ex}')

@router.post('/{workflow_id}/reject')
def reject(workflow_id: int, reason: str = Form(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf: raise HTTPException(404, 'Workflow not found')
    step = db.query(WorkflowSigner).filter(WorkflowSigner.workflow_id == workflow_id, WorkflowSigner.signing_order == wf.current_step).first()
    if not step or step.signer_user_id != user.id: raise HTTPException(403, 'Not your step')
    step.status = 'rejected'; step.rejected_at = datetime.utcnow(); step.reject_reason = reason; wf.status = 'Rejected'
    doc = db.query(Document).filter(Document.id == wf.document_id).first(); doc.status = 'Rejected'
    add_audit(db, 'SIGN_REJECTED', user.id, doc.id, reason)
    db.commit(); return {"status": "Rejected"}
