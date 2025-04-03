from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.api.v1 import auth, users, links
from app.db.session import database_engine
from app.db.base import BaseModel
from app.services.links_service import UrlService
from app.settings.config import config
import asyncio
import logging

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

app = FastAPI(
    title=config.PROJECT_NAME,
    description=config.PROJECT_DESCRIPTION,
    version=config.VERSION,
    docs_url=config.DOCS_URL,
    openapi_url=config.OPENAPI_URL,
    root_path="/api"
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(links.router, prefix="/api")

scheduler = AsyncIOScheduler()

@app.get("/api/health")
async def health():
    return {"status": "Service is running"}

@app.on_event("startup")
async def initialize_app():
    retries = 5
    for attempt in range(retries):
        try:
            async with database_engine.begin() as connection:
                await connection.run_sync(BaseModel.metadata.create_all)
            logger.info("Database initialized successfully")
            scheduler.add_job(UrlService.cleanup_expired_urls, 'interval', hours=24, args=[app.state.db_session])
            scheduler.start()
            break
        except Exception as error:
            logger.warning(f"Database connection failed, retrying... ({attempt + 1}/{retries})")
            await asyncio.sleep(2)
    else:
        logger.error("Failed to initialize database after retries")
        raise Exception("Database initialization failed")

@app.on_event("shutdown")
async def shutdown_app():
    scheduler.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)