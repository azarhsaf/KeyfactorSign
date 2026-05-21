import os
import shutil
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.session import Base, engine, get_db
from app.models.models import User, Document, Workflow, WorkflowSigner, AuditLog
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings

Base.metadata.create_all(bind=engine)
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.signed_dir, exist_ok=True)

app = FastAPI(title="SignPortal API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.get('/api/health')
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.post('/api/register')
def register(username: str = Form(...), email: str = Form(...), password: str = Form(...), role: str = Form("signer"), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(400, "Username exists")
    u = User(username=username, email=email, display_name=username, role=role, password_hash=hash_password(password))
    db.add(u)
    db.commit()
    return {"message": "created"}


@app.post('/api/login')
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_access_token({"sub": user.username, "role": user.role}), "token_type": "bearer"}


@app.get('/api/me')
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "role": user.role}


@app.post('/api/documents/upload')
def upload_document(document_name: str = Form(...), workflow_type: str = Form("single"), signer_ids: str = Form(...), file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, 'Only PDF supported')
    path = os.path.join(settings.upload_dir, f"{int(datetime.utcnow().timestamp())}_{file.filename}")
    with open(path, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    doc = Document(document_name=document_name, original_file_path=path, uploaded_by=user.id)
    db.add(doc); db.commit(); db.refresh(doc)
    wf = Workflow(document_id=doc.id, workflow_type=workflow_type)
    db.add(wf); db.commit(); db.refresh(wf)
    ids = [int(x) for x in signer_ids.split(',')]
    for i, sid in enumerate(ids, start=1):
        db.add(WorkflowSigner(workflow_id=wf.id, signer_user_id=sid, signing_order=i, status='pending'))
    db.add(AuditLog(document_id=doc.id, user_id=user.id, action='UPLOAD', details=f'Workflow {workflow_type}'))
    db.commit()
    return {"document_id": doc.id, "workflow_id": wf.id}


@app.get('/api/documents')
def list_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    return docs


@app.post('/api/workflows/{workflow_id}/sign')
def sign_step(workflow_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(404, 'Not found')
    step = db.query(WorkflowSigner).filter(WorkflowSigner.workflow_id == workflow_id, WorkflowSigner.signing_order == wf.current_step).first()
    if not step or step.signer_user_id != user.id:
        raise HTTPException(403, 'Not your step')
    step.status = 'signed'; step.signed_at = datetime.utcnow()
    doc = db.query(Document).filter(Document.id == wf.document_id).first()
    signed_path = os.path.join(settings.signed_dir, f"signed_{doc.id}_step{wf.current_step}.pdf")
    shutil.copy(doc.original_file_path if wf.current_step == 1 else doc.signed_file_path, signed_path)
    doc.signed_file_path = signed_path
    total = db.query(WorkflowSigner).filter(WorkflowSigner.workflow_id == workflow_id).count()
    if wf.current_step >= total:
        wf.status = 'Completed'; doc.status = 'Completed'
    else:
        wf.current_step += 1
        wf.status = f"Signed by User {wf.current_step - 1}"
    db.add(AuditLog(document_id=doc.id, user_id=user.id, action='SIGN', details=f'Step {step.signing_order}'))
    db.commit()
    return {"status": wf.status, "signed_file": doc.signed_file_path}


@app.get('/api/audit/{document_id}')
def audit(document_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(AuditLog).filter(AuditLog.document_id == document_id).all()
