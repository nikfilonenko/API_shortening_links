from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.user import Account
from app.schemas.user import AccountSignup, AccountInfo
from app.services.auth_service import AuthService
from app.db.crud import CRUD


class UserManager:
    @staticmethod
    async def register_account(session: AsyncSession, signup_data: AccountSignup) -> AccountInfo:
        if await CRUD.get_account_by_login(session, signup_data.login):
            raise HTTPException(status_code=400, detail="Login already taken")
        if signup_data.email_address and (await session.execute(
                select(Account).where(Account.email_address == signup_data.email_address))).scalars().first():
            raise HTTPException(status_code=400, detail="Email already registered")

        new_account = Account(
            login=signup_data.login,
            email_address=signup_data.email_address,
            password_encrypted=AuthService.hash_password(signup_data.password)
        )
        session.add(new_account)
        await session.commit()
        await session.refresh(new_account)
        return AccountInfo.from_orm(new_account)

    @staticmethod
    async def get_account_info(session: AsyncSession, account: Account) -> AccountInfo:
        return AccountInfo.from_orm(account)