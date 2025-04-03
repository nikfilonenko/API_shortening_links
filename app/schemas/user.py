from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class AccountBase(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    email_address: Optional[EmailStr] = None

class AccountSignup(AccountBase):
    password: str = Field(..., min_length=8)

class AccountInfo(AccountBase):
    account_id: int
    signup_date: datetime
    is_enabled: bool
    account_role: str

    class Config:
        from_attributes = True

class AuthToken(BaseModel):
    token: str
    token_kind: str = "bearer"