from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="signer")
    auth_source = Column(String(20), nullable=False, default="local")
    is_active = Column(Boolean, default=True)
    must_change_password = Column(Boolean, default=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
