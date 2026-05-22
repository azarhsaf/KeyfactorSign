from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from app.database import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    document_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    original_file_path = Column(String(500), nullable=False)
    current_file_path = Column(String(500), nullable=False)
    signed_file_path = Column(String(500), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="Draft")
    file_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
