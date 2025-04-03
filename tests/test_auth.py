from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from app.schemas.user import AuthToken
from app.services.auth_service import AuthService

@pytest.mark.asyncio
async def test_login(client: TestClient, mock_session, mock_account, override_get_session):
    AuthService.validate_user = AsyncMock(return_value=mock_account)
    AuthService.generate_token = lambda payload: "mock_jwt_token"

    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert response.json() == {"token": "mock_jwt_token", "token_kind": "bearer"}