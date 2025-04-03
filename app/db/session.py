from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.settings.config import config

database_engine = create_async_engine(config.DB_CONNECTION, echo=False)
SessionFactory = async_sessionmaker(database_engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with SessionFactory() as session:
        yield session