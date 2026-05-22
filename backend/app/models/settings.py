from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base

class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    category = Column(String(50), nullable=False)
    key = Column(String(100), nullable=False)
    value_encrypted = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
