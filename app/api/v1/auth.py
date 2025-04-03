from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import AuthToken
from app.services.auth_service import AuthService
from app.db.session import get_session

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=AuthToken)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    account = await AuthService.validate_user(session, form.username, form.password)
    token = AuthService.generate_token({"sub": account.login})
    return AuthToken(token=token)