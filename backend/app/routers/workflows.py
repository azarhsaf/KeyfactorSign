from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Workflow, WorkflowSigner, Document, SigningJob
from app.auth.dependencies import get_current_user
from app.services.signserver_connector import SignServerConnector
from app.services.pdf_service import timestamp_presence_placeholder

router=APIRouter(prefix='/api/workflows', tags=['workflows'])

@router.post('')
def create_workflow(): return {"message":"Use /api/documents/upload"}

@router.get('/{workflow_id}')
def get_workflow(workflow_id:int, db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(Workflow).filter(Workflow.id==workflow_id).first()

@router.post('/{workflow_id}/sign')
def sign(workflow_id:int, db:Session=Depends(get_db), user=Depends(get_current_user)):
    wf=db.query(Workflow).filter(Workflow.id==workflow_id).first()
    step=db.query(WorkflowSigner).filter(WorkflowSigner.workflow_id==workflow_id, WorkflowSigner.signing_order==wf.current_step).first()
    if not step or step.signer_user_id!=user.id: raise HTTPException(403,'Not your step')
    doc=db.query(Document).filter(Document.id==wf.document_id).first()
    out=doc.current_file_path.replace('.pdf', f'_step{wf.current_step}_signed.pdf')
    job=SigningJob(document_id=doc.id, workflow_signer_id=step.id, status='running'); db.add(job); db.commit(); db.refresh(job)
    try:
        SignServerConnector().sign_pdf(doc.current_file_path, out, {"username": user.username})
        step.status='signed'; step.signed_at=datetime.utcnow(); doc.current_file_path=out; doc.signed_file_path=out
        total=db.query(WorkflowSigner).filter(WorkflowSigner.workflow_id==workflow_id).count()
        if wf.current_step>=total: wf.status='Completed'; doc.status='Completed'
        else: wf.current_step+=1; wf.status='In Progress'; doc.status='In Progress'
        job.status='success'
        ts=timestamp_presence_placeholder(out)
        db.commit(); return {"status": wf.status, "timestamp": ts}
    except Exception as ex:
        job.status='failed'; job.error_message=str(ex); doc.status='Failed'; wf.status='Failed'; db.commit()
        raise HTTPException(502, f'SignServer signing failed: {ex}')

@router.post('/{workflow_id}/reject')
def reject(workflow_id:int, reason:str=Form(...), db:Session=Depends(get_db), user=Depends(get_current_user)):
    wf=db.query(Workflow).filter(Workflow.id==workflow_id).first()
    step=db.query(WorkflowSigner).filter(WorkflowSigner.workflow_id==workflow_id, WorkflowSigner.signing_order==wf.current_step).first()
    if step.signer_user_id!=user.id: raise HTTPException(403,'Not your step')
    step.status='rejected'; step.rejected_at=datetime.utcnow(); step.reject_reason=reason; wf.status='Rejected';
    doc=db.query(Document).filter(Document.id==wf.document_id).first(); doc.status='Rejected'; db.commit(); return {"status":"Rejected"}
