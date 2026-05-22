import os, shutil
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models import Document, Workflow, WorkflowSigner, SignaturePlacement
from app.auth.dependencies import get_current_user
from app.services.pdf_service import validate_pdf, hash_file

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post('/upload')
def upload(document_name: str = Form(...), description: str = Form(''), workflow_type: str = Form(...), signer_ids: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, 'PDF only')
    content = file.file.read()
    if len(content) > settings.max_file_mb*1024*1024:
        raise HTTPException(400, 'File too large')
    path = os.path.join(settings.upload_dir, f"{int(datetime.utcnow().timestamp())}_{file.filename}")
    with open(path,'wb') as f: f.write(content)
    validate_pdf(path)
    h = hash_file(path)
    doc = Document(document_name=document_name, description=description, original_file_path=path, current_file_path=path, uploaded_by=user.id, status='Pending Signature', file_hash=h)
    db.add(doc); db.commit(); db.refresh(doc)
    wf = Workflow(document_id=doc.id, workflow_type=workflow_type, status='Pending Signature')
    db.add(wf); db.commit(); db.refresh(wf)
    for i,sid in enumerate([int(x) for x in signer_ids.split(',')], start=1):
        db.add(WorkflowSigner(workflow_id=wf.id, signer_user_id=sid, signing_order=i))
    db.commit()
    return {"document_id": doc.id, "workflow_id": wf.id}

@router.get('')
def list_docs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Document).all()

@router.get('/{document_id}')
def get_doc(document_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Document).filter(Document.id==document_id).first()

@router.get('/{document_id}/download-original')
def d1(document_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    d=db.query(Document).filter(Document.id==document_id).first(); return FileResponse(d.original_file_path)
@router.get('/{document_id}/download-signed')
def d2(document_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    d=db.query(Document).filter(Document.id==document_id).first(); return FileResponse(d.signed_file_path)
@router.get('/{document_id}/preview')
def pv(document_id:int, db:Session=Depends(get_db), user=Depends(get_current_user)):
    d=db.query(Document).filter(Document.id==document_id).first(); return FileResponse(d.current_file_path, media_type='application/pdf')

@router.post('/{document_id}/signature-placement')
def place(document_id:int, workflow_signer_id:int=Form(...), page_number:int=Form(...), x:float=Form(...), y:float=Form(...), width:float=Form(...), height:float=Form(...), signature_text:str=Form(''), db:Session=Depends(get_db), user=Depends(get_current_user)):
    p=SignaturePlacement(document_id=document_id, workflow_signer_id=workflow_signer_id, page_number=page_number, x=x,y=y,width=width,height=height,signature_text=signature_text)
    db.add(p); db.commit(); return {"message":"saved"}
