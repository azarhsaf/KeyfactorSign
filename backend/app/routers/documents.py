import os
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models import Document, Workflow, WorkflowSigner, SignaturePlacement, User
from app.auth.dependencies import get_current_user
from app.services.pdf_service import validate_pdf, hash_file
from app.services.audit_service import add_audit

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _doc_to_json(d: Document, db: Session):
    uploader = db.query(User).filter(User.id == d.uploaded_by).first()
    wf = db.query(Workflow).filter(Workflow.document_id == d.id).first()
    current_signer = None
    if wf:
        ws = db.query(WorkflowSigner).filter(WorkflowSigner.workflow_id == wf.id, WorkflowSigner.signing_order == wf.current_step).first()
        if ws:
            su = db.query(User).filter(User.id == ws.signer_user_id).first()
            current_signer = su.display_name if su else None
    return {
        "id": d.id, "document_name": d.document_name, "description": d.description,
        "status": d.status, "uploaded_by": d.uploaded_by, "uploaded_by_name": uploader.display_name if uploader else "-",
        "current_signer": current_signer, "created_at": d.created_at.isoformat() if d.created_at else None,
        "signed_file_path": d.signed_file_path
    }


@router.post('/upload')
def upload(document_name: str = Form(...), description: str = Form(''), workflow_type: str = Form(...), signer_ids: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, 'PDF only')
    content = file.file.read()
    if len(content) > settings.max_file_mb * 1024 * 1024:
        raise HTTPException(400, 'File too large')
    os.makedirs(settings.upload_dir, exist_ok=True)
    path = os.path.join(settings.upload_dir, f"{int(datetime.utcnow().timestamp())}_{file.filename}")
    with open(path, 'wb') as f:
        f.write(content)
    validate_pdf(path)
    h = hash_file(path)
    doc = Document(document_name=document_name, description=description, original_file_path=path, current_file_path=path, uploaded_by=user.id, status='Pending Signature', file_hash=h)
    db.add(doc); db.commit(); db.refresh(doc)
    wf = Workflow(document_id=doc.id, workflow_type=workflow_type, status='Pending Signature')
    db.add(wf); db.commit(); db.refresh(wf)
    signer_list = [int(x.strip()) for x in signer_ids.split(',') if x.strip()]
    if not signer_list:
        raise HTTPException(400, 'At least one signer required')
    for i, sid in enumerate(signer_list, start=1):
        db.add(WorkflowSigner(workflow_id=wf.id, signer_user_id=sid, signing_order=i, status='pending'))
    db.commit()
    add_audit(db, 'UPLOAD_DOCUMENT', user.id, doc.id, f'workflow={workflow_type} signers={signer_ids}')
    return {"document_id": doc.id, "workflow_id": wf.id}


@router.get('')
def list_docs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [_doc_to_json(d, db) for d in db.query(Document).order_by(Document.id.desc()).all()]


@router.get('/pending')
def pending_docs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(WorkflowSigner).filter(WorkflowSigner.signer_user_id == user.id, WorkflowSigner.status == 'pending').all()
    out = []
    for r in rows:
        wf = db.query(Workflow).filter(Workflow.id == r.workflow_id).first()
        if wf and wf.current_step == r.signing_order:
            d = db.query(Document).filter(Document.id == wf.document_id).first()
            out.append(_doc_to_json(d, db) | {"workflow_id": wf.id, "step_id": r.id, "signing_order": r.signing_order})
    return out


@router.get('/completed')
def completed_docs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [_doc_to_json(d, db) for d in db.query(Document).filter(Document.status == 'Completed').order_by(Document.id.desc()).all()]


@router.get('/{document_id}')
def get_doc(document_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    d = db.query(Document).filter(Document.id == document_id).first()
    if not d:
        raise HTTPException(404, 'Document not found')
    return _doc_to_json(d, db)


@router.get('/{document_id}/download-original')
def d1(document_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    d = db.query(Document).filter(Document.id == document_id).first()
    if not d: raise HTTPException(404, 'Not found')
    add_audit(db, 'DOWNLOAD_ORIGINAL', user.id, d.id)
    return FileResponse(d.original_file_path)


@router.get('/{document_id}/download-signed')
def d2(document_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    d = db.query(Document).filter(Document.id == document_id).first()
    if not d or not d.signed_file_path: raise HTTPException(404, 'Signed file not available')
    add_audit(db, 'DOWNLOAD_SIGNED', user.id, d.id)
    return FileResponse(d.signed_file_path)


@router.get('/{document_id}/preview')
def pv(document_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    d = db.query(Document).filter(Document.id == document_id).first()
    if not d: raise HTTPException(404, 'Not found')
    return FileResponse(d.current_file_path, media_type='application/pdf')


@router.post('/{document_id}/signature-placement')
def place(document_id: int, workflow_signer_id: int = Form(...), page_number: int = Form(...), x: float = Form(...), y: float = Form(...), width: float = Form(...), height: float = Form(...), signature_text: str = Form(''), db: Session = Depends(get_db), user=Depends(get_current_user)):
    p = SignaturePlacement(document_id=document_id, workflow_signer_id=workflow_signer_id, page_number=page_number, x=x, y=y, width=width, height=height, signature_text=signature_text)
    db.add(p); db.commit()
    add_audit(db, 'SAVE_SIGNATURE_PLACEMENT', user.id, document_id)
    return {"message": "saved"}


@router.get('/my')
def my_docs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [_doc_to_json(d, db) for d in db.query(Document).filter(Document.uploaded_by == user.id).order_by(Document.id.desc()).all()]

@router.get('/failed')
def failed_docs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [_doc_to_json(d, db) for d in db.query(Document).filter(Document.status == 'Failed').order_by(Document.id.desc()).all()]

@router.get('/{document_id}/preview-original')
def preview_original(document_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    d = db.query(Document).filter(Document.id == document_id).first()
    if not d: raise HTTPException(404, 'Not found')
    return FileResponse(d.original_file_path, media_type='application/pdf')

@router.get('/{document_id}/preview-signed')
def preview_signed(document_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    d = db.query(Document).filter(Document.id == document_id).first()
    if not d or not d.signed_file_path: raise HTTPException(404, 'Signed file not available')
    return FileResponse(d.signed_file_path, media_type='application/pdf')


@router.get('/{document_id}/signature-placement')
def get_placements(document_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(SignaturePlacement).filter(SignaturePlacement.document_id == document_id).all()
    return [{
        "id": r.id,
        "workflow_signer_id": r.workflow_signer_id,
        "page_number": r.page_number,
        "x": r.x,
        "y": r.y,
        "width": r.width,
        "height": r.height,
        "signature_text": r.signature_text,
    } for r in rows]
