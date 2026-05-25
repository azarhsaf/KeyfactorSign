from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from app.database import Base

class Setting(Base):
    __tablename__ = "app_settings"
    id = Column(Integer, primary_key=True)
    category = Column(String(50), nullable=False)
    key = Column(String(100), nullable=False)
    value_encrypted = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class LDAPGroupMapping(Base):
    __tablename__ = "ldap_group_mappings"
    id = Column(Integer, primary_key=True)
    role = Column(String(50), nullable=False)
    group_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class EmailLog(Base):
    __tablename__ = "email_logs"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, nullable=True)
    recipient = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    status = Column(String(30), default="queued")
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
