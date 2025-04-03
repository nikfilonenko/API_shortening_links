import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.models.user import Account
from app.db.session import get_session
from unittest.mock import AsyncMock

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
async def mock_session():
    session = AsyncMock(spec=AsyncSession)
    return session

@pytest.fixture
def mock_account():
    return Account(
        account_id=1,
        login="testuser",
        email_address="test@example.com",
        password_encrypted="hashed_password",
        signup_date="2023-01-01T00:00:00",
        is_enabled=True,
        account_role="regular"
    )

@pytest.fixture
def override_get_session(mock_session):
    async def _override_get_session():
        yield mock_session
    app.dependency_overrides[get_session] = _override_get_session
    return _override_get_session

@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()