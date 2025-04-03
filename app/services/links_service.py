import random
import string
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.link import ShortenedUrl, UrlVisit, UrlArchive
from app.models.user import Account
from app.schemas.link import UrlCreate, UrlInfo, UrlUpdate, UrlStats, UrlSearchResult
from app.db.crud import CRUD
from app.db.redis_cache import set_cache, get_cache, delete_cache
from app.settings.config import config


class UrlService:
    @staticmethod
    def create_short_key(length: int = 7) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    async def generate_url(session: AsyncSession, url_data: UrlCreate, creator: Account | None) -> UrlInfo:
        if url_data.custom_key:
            if await CRUD.get_url_by_key(session, url_data.custom_key):
                raise HTTPException(status_code=400, detail="Custom key already in use")
            short_key = url_data.custom_key
        else:
            short_key = UrlService.create_short_key()
            while await CRUD.get_url_by_key(session, short_key):
                short_key = UrlService.create_short_key()

        new_url = ShortenedUrl(
            short_key=short_key,
            full_url=str(url_data.full_url),
            custom_key=url_data.custom_key,
            expiry_time=url_data.expiry_time,
            category=url_data.category,
            auto_extend=url_data.auto_extend,
            creator_id=creator.account_id if creator else None
        )
        session.add(new_url)
        await session.commit()
        await session.refresh(new_url)
        return UrlInfo.from_orm(new_url)

    @staticmethod
    async def redirect_url(session: AsyncSession, short_key: str, request: Request) -> str:
        cached = await get_cache(f"url:{short_key}")
        if cached:
            return cached["full_url"]

        url_record = await CRUD.get_url_by_key(session, short_key)
        if not url_record:
            raise HTTPException(status_code=404, detail="URL not found")
        if url_record.expiry_time and url_record.expiry_time < datetime.utcnow():
            raise HTTPException(status_code=410, detail="URL expired")

        url_record.hit_count += 1
        url_record.last_hit_time = datetime.utcnow()
        visit = UrlVisit(
            url_id=url_record.url_id,
            visitor_ip=request.client.host,
            visitor_agent=request.headers.get("User-Agent")
        )
        session.add(visit)
        await session.commit()

        await set_cache(f"url:{short_key}", {"full_url": url_record.full_url}, ttl=7200)
        return url_record.full_url

    @staticmethod
    async def update_url(session: AsyncSession, short_key: str, update_data: UrlUpdate,
                         user: Account | None) -> UrlInfo:
        url_record = await CRUD.get_url_by_key(session, short_key)
        if not url_record:
            raise HTTPException(status_code=404, detail="URL not found")
        if url_record.creator_id and (not user or url_record.creator_id != user.account_id):
            raise HTTPException(status_code=403, detail="Permission denied")

        if update_data.full_url:
            url_record.full_url = str(update_data.full_url)
        if update_data.expiry_time is not None:
            url_record.expiry_time = update_data.expiry_time
        if update_data.category is not None:
            url_record.category = update_data.category
        if update_data.auto_extend is not None:
            url_record.auto_extend = update_data.auto_extend

        await session.commit()
        await delete_cache(f"url:{short_key}")
        return UrlInfo.from_orm(url_record)

    @staticmethod
    async def delete_url(session: AsyncSession, short_key: str, user: Account | None):
        url_record = await CRUD.get_url_by_key(session, short_key)
        if not url_record:
            raise HTTPException(status_code=404, detail="URL not found")
        if url_record.creator_id and (not user or url_record.creator_id != user.account_id):
            raise HTTPException(status_code=403, detail="Permission denied")

        archive = UrlArchive(
            url_id=url_record.url_id,
            short_key=url_record.short_key,
            full_url=url_record.full_url,
            archive_reason="user_deleted"
        )
        session.add(archive)
        await session.delete(url_record)
        await session.commit()
        await delete_cache(f"url:{short_key}")

    @staticmethod
    async def get_url_stats(session: AsyncSession, short_key: str) -> UrlStats:
        url_record = await CRUD.get_url_by_key(session, short_key)
        if not url_record:
            raise HTTPException(status_code=404, detail="URL not found")

        daily_stats = await CRUD.get_daily_stats(session, url_record.url_id)
        stats = UrlStats.from_orm(url_record)
        stats.daily_stats = [{"date": date, "hits": count} for date, count in daily_stats]
        return stats

    @staticmethod
    async def search_url(session: AsyncSession, full_url: str) -> UrlSearchResult:
        cached = await get_cache(f"search:{full_url}")
        if cached:
            return UrlSearchResult(**cached)

        url_record = await CRUD.get_url_by_full_url(session, full_url)
        if not url_record:
            raise HTTPException(status_code=404, detail="URL not found")

        result = UrlSearchResult(short_key=url_record.short_key, full_url=url_record.full_url)
        await set_cache(f"search:{full_url}", result.dict(), ttl=600)
        return result

    @staticmethod
    async def get_category_urls(session: AsyncSession, category: str) -> list[UrlInfo]:
        urls = await CRUD.get_urls_by_category(session, category)
        return [UrlInfo.from_orm(url) for url in urls]

    @staticmethod
    async def cleanup_expired_urls(session: AsyncSession):
        expired_urls = await CRUD.get_expired_urls(session)
        for url in expired_urls:
            archive = UrlArchive(
                url_id=url.url_id,
                short_key=url.short_key,
                full_url=url.full_url,
                archive_reason="expired"
            )
            session.add(archive)
            await session.delete(url)
            await delete_cache(f"url:{url.short_key}")
        await session.commit()