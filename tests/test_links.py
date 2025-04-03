from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from app.schemas.link import UrlCreate, UrlInfo, UrlUpdate, UrlStats, UrlSearchResult
from app.services.links_service import UrlService
from app.services.auth_service import AuthService

@pytest.mark.asyncio
async def test_create_url(client: TestClient, mock_session, mock_account, override_get_session):
    url_data = {"full_url": "https://example.com", "custom_key": "testkey"}
    mock_url_info = UrlInfo(
        url_id=1, short_key="testkey", full_url="https://example.com", creation_time="2023-01-01T00:00:00",
        hit_count=0, last_hit_time=None, creator_id=1
    )
    UrlService.generate_url = AsyncMock(return_value=mock_url_info)
    AuthService.optional_decode_token = AsyncMock(return_value=mock_account)

    response = client.post("/api/links/create", json=url_data, headers={"Authorization": "Bearer token"})
    assert response.status_code == 200
    assert response.json()["short_key"] == "testkey"

@pytest.mark.asyncio
async def test_redirect(client: TestClient, mock_session, override_get_session):
    UrlService.redirect_url = AsyncMock(return_value="https://example.com")

    response = client.get("/api/links/testkey", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["Location"] == "https://example.com"

@pytest.mark.asyncio
async def test_update_url(client: TestClient, mock_session, mock_account, override_get_session):
    update_data = {"full_url": "https://newexample.com"}
    mock_url_info = UrlInfo(
        url_id=1, short_key="testkey", full_url="https://newexample.com", creation_time="2023-01-01T00:00:00",
        hit_count=0, last_hit_time=None, creator_id=1
    )
    UrlService.update_url = AsyncMock(return_value=mock_url_info)
    AuthService.optional_decode_token = AsyncMock(return_value=mock_account)

    response = client.put("/api/links/testkey", json=update_data, headers={"Authorization": "Bearer token"})
    assert response.status_code == 200
    assert response.json()["full_url"] == "https://newexample.com"

@pytest.mark.asyncio
async def test_remove_url(client: TestClient, mock_session, mock_account, override_get_session):
    UrlService.delete_url = AsyncMock()
    AuthService.optional_decode_token = AsyncMock(return_value=mock_account)

    response = client.delete("/api/links/testkey", headers={"Authorization": "Bearer token"})
    assert response.status_code == 200
    assert response.json() == {"message": "URL deleted"}

@pytest.mark.asyncio
async def test_url_stats(client: TestClient, mock_session, override_get_session):
    mock_stats = UrlStats(
        url_id=1, short_key="testkey", full_url="https://example.com", creation_time="2023-01-01T00:00:00",
        hit_count=5, last_hit_time="2023-01-02T00:00:00", daily_stats=[{"date": "2023-01-01", "hits": 5}]
    )
    UrlService.get_url_stats = AsyncMock(return_value=mock_stats)

    response = client.get("/api/links/testkey/stats")
    assert response.status_code == 200
    assert response.json()["hit_count"] == 5

@pytest.mark.asyncio
async def test_search_url(client: TestClient, mock_session, override_get_session):
    mock_search_result = UrlSearchResult(short_key="testkey", full_url="https://example.com")
    UrlService.search_url = AsyncMock(return_value=mock_search_result)

    response = client.get("/api/links/search?full_url=https://example.com")
    assert response.status_code == 200
    assert response.json()["short_key"] == "testkey"

@pytest.mark.asyncio
async def test_get_category_urls(client: TestClient, mock_session, override_get_session):
    mock_urls = [
        UrlInfo(url_id=1, short_key="testkey1", full_url="https://example.com", creation_time="2023-01-01T00:00:00"),
        UrlInfo(url_id=2, short_key="testkey2", full_url="https://example2.com", creation_time="2023-01-01T00:00:00")
    ]
    UrlService.get_category_urls = AsyncMock(return_value=mock_urls)

    response = client.get("/api/links/category/testcategory")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["short_key"] == "testkey1"