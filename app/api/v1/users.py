from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from app.models.user import Account
from app.schemas.user import AccountSignup, AccountInfo
from app.services.user_service import UserManager
from app.services.auth_service import AuthService
from app.db.session import get_session

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/signup", response_model=AccountInfo)
async def signup(
    signup_data: AccountSignup,
    session: AsyncSession = Depends(get_session)
):
    return await UserManager.register_account(session, signup_data)

@router.get("/profile", response_model=AccountInfo)
async def profile(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme)
):
    account = await AuthService.decode_token(token, session)
    return await UserManager.get_account_info(session, account)