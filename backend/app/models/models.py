from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="signer")
    password_hash = Column(String(255), nullable=False)
    ldap_user_flag = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    document_name = Column(String(255), nullable=False)
    original_file_path = Column(String(500), nullable=False)
    signed_file_path = Column(String(500), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="Uploaded")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    workflow_type = Column(String(50), nullable=False)
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
    status = Column(String(50), default="pending")
    signed_at = Column(DateTime, nullable=True)
    signature_page = Column(Integer, default=1)
    signature_x = Column(Integer, default=100)
    signature_y = Column(Integer, default=100)
    signature_width = Column(Integer, default=200)
    signature_height = Column(Integer, default=80)
    signature_text = Column(Text, default="")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
