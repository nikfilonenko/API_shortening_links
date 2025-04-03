from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import BaseModel

class Account(BaseModel):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, nullable=False)
    email_address = Column(String(100), unique=True, nullable=True)
    password_encrypted = Column(String(255), nullable=False)
    signup_date = Column(DateTime, server_default=func.now())
    is_enabled = Column(Boolean, default=True)
    account_role = Column(String(20), default="regular")