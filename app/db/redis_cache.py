import redis.asyncio as redis
from app.settings.config import config
import json
import logging

logger = logging.getLogger("redis")

redis_instance = redis.from_url(config.REDIS_CONNECTION)

async def fetch_redis_client():
    try:
        await redis_instance.ping()
        return redis_instance
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return None

async def set_cache(key: str, value: dict, ttl: int = 3600):
    client = await fetch_redis_client()
    if client:
        await client.set(key, json.dumps(value), ex=ttl)

async def get_cache(key: str) -> dict | None:
    client = await fetch_redis_client()
    if client:
        data = await client.get(key)
        return json.loads(data) if data else None
    return None

async def delete_cache(key: str):
    client = await fetch_redis_client()
    if client:
        await client.delete(key)