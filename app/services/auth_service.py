from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud import CRUD
from app.models.user import Account
from app.settings.config import config

pwd_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_auth = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class AuthService:
    @staticmethod
    def hash_password(raw_password: str) -> str:
        return pwd_hasher.hash(raw_password)

    @staticmethod
    def check_password(raw_password: str, hashed_password: str) -> bool:
        return pwd_hasher.verify(raw_password, hashed_password)

    @staticmethod
    def generate_token(data: dict, expires_in: timedelta = None) -> str:
        payload = data.copy()
        expiry = datetime.utcnow() + (expires_in or timedelta(minutes=config.TOKEN_LIFETIME_MINUTES))
        payload["exp"] = expiry
        return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

    @staticmethod
    async def validate_user(session: AsyncSession, login: str, password: str) -> 'Account':
        account = await CRUD.get_account_by_login(session, login)
        if not account or not AuthService.check_password(password, account.password_encrypted):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return account

    @staticmethod
    async def decode_token(token: str, session: AsyncSession) -> Account:
        try:
            payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
            login = payload.get("sub")
            if not login:
                raise HTTPException(status_code=401, detail="Invalid token")
            account = await CRUD.get_account_by_login(session, login)
            if not account:
                raise HTTPException(status_code=401, detail="User not found")
            return account
        except JWTError:
            raise HTTPException(status_code=401, detail="Token validation failed")

    @staticmethod
    async def optional_decode_token(token: str | None, session: AsyncSession) -> 'Account | None':
        if not token:
            return None
        return await AuthService.decode_token(token, session)