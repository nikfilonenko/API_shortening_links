from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.user import Account
from app.models.link import ShortenedUrl, UrlVisit, UrlArchive

class CRUD:
    @staticmethod
    async def get_account_by_login(session: AsyncSession, login: str) -> Account | None:
        query = select(Account).where(Account.login == login)
        result = await session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_url_by_key(session: AsyncSession, short_key: str) -> ShortenedUrl | None:
        query = select(ShortenedUrl).where(ShortenedUrl.short_key == short_key)
        result = await session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_url_by_full_url(session: AsyncSession, full_url: str) -> ShortenedUrl | None:
        query = select(ShortenedUrl).where(ShortenedUrl.full_url == full_url)
        result = await session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_urls_by_category(session: AsyncSession, category: str) -> list[ShortenedUrl]:
        query = select(ShortenedUrl).where(ShortenedUrl.category == category)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_expired_urls(session: AsyncSession) -> list[ShortenedUrl]:
        query = select(ShortenedUrl).where(ShortenedUrl.expiry_time < func.now())
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_daily_stats(session: AsyncSession, url_id: int) -> list[tuple]:
        query = select(UrlVisit.visit_date, func.count(UrlVisit.visit_id)).where(UrlVisit.url_id == url_id).group_by(UrlVisit.visit_date).order_by(UrlVisit.visit_date)
        result = await session.execute(query)
        return result.all()