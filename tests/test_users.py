from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from app.schemas.user import AccountSignup, AccountInfo
from app.services.user_service import UserManager
from app.services.auth_service import AuthService

@pytest.mark.asyncio
async def test_signup(client: TestClient, mock_session, override_get_session):
    signup_data = {"login": "testuser", "password": "testpass123", "email_address": "test@example.com"}
    mock_account_info = AccountInfo(
        account_id=1, login="testuser", email_address="test@example.com",
        signup_date="2023-01-01T00:00:00", is_enabled=True, account_role="regular"
    )
    mock_session.commit = AsyncMock()
    UserManager.register_account = AsyncMock(return_value=mock_account_info)

    response = client.post("/api/users/signup", json=signup_data)
    assert response.status_code == 200
    assert response.json() == mock_account_info.dict()

@pytest.mark.asyncio
async def test_profile(client: TestClient, mock_session, mock_account, override_get_session):
    token = "mock_jwt_token"
    AuthService.decode_token = AsyncMock(return_value=mock_account)
    UserManager.get_account_info = AsyncMock(return_value=AccountInfo.from_orm(mock_account))

    response = client.get("/api/users/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["login"] == "testuser"