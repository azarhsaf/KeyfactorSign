from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from app.database import Base

class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    workflow_type = Column(String(30), nullable=False)
    current_step = Column(Integer, default=1)
    status = Column(String(50), default="Pending Signature")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class WorkflowSigner(Base):
    __tablename__ = "workflow_signers"
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    signer_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    signing_order = Column(Integer, nullable=False)
    status = Column(String(30), default="pending")
    signed_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    reject_reason = Column(Text, nullable=True)

class SignaturePlacement(Base):
    __tablename__ = "signature_placements"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    workflow_signer_id = Column(Integer, ForeignKey("workflow_signers.id"), nullable=False)
    page_number = Column(Integer, default=1)
    x = Column(Float, default=100)
    y = Column(Float, default=100)
    width = Column(Float, default=220)
    height = Column(Float, default=80)
    signature_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SigningJob(Base):
    __tablename__ = "signing_jobs"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    workflow_signer_id = Column(Integer, ForeignKey("workflow_signers.id"), nullable=False)
    status = Column(String(30), default="queued")
    signserver_request_id = Column(String(200), nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
