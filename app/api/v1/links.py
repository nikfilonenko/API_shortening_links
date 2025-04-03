from fastapi import APIRouter, Depends, Response, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.link import UrlCreate, UrlInfo, UrlUpdate, UrlStats, UrlSearchResult
from app.services.links_service import UrlService
from app.services.auth_service import AuthService
from app.db.session import get_session
from app.models.user import Account

router = APIRouter(prefix="/links", tags=["links"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/create", response_model=UrlInfo)
async def create_link(
    url_data: UrlCreate,
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme)
):
    account = None
    if token:
        account = await AuthService.decode_token(token, session)
    return await UrlService.generate_url(session, url_data, account)

@router.get("/{short_key}")
async def redirect(
    short_key: str,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    target_url = await UrlService.redirect_url(session, short_key, request)
    return Response(status_code=307, headers={"Location": target_url})

@router.put("/{short_key}", response_model=UrlInfo)
async def update_url(
    short_key: str,
    update_data: UrlUpdate,
    session: AsyncSession = Depends(get_session),
    user: Account | None = Depends(AuthService.optional_decode_token)
):
    return await UrlService.update_url(session, short_key, update_data, user)

@router.delete("/{short_key}")
async def remove_url(
    short_key: str,
    session: AsyncSession = Depends(get_session),
    user: Account | None = Depends(AuthService.optional_decode_token)
):
    await UrlService.delete_url(session, short_key, user)
    return {"message": "URL deleted"}

@router.get("/{short_key}/stats", response_model=UrlStats)
async def url_stats(
    short_key: str,
    session: AsyncSession = Depends(get_session)
):
    return await UrlService.get_url_stats(session, short_key)

@router.get("/search", response_model=UrlSearchResult)
async def search_url(
    full_url: str,
    session: AsyncSession = Depends(get_session)
):
    return await UrlService.search_url(session, full_url)

@router.get("/category/{category}", response_model=List[UrlInfo])
async def get_category_urls(
    category: str,
    session: AsyncSession = Depends(get_session)
):
    return await UrlService.get_category_urls(session, category)