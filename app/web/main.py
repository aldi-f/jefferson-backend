import logging
import time
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException

from app.clients.redis.client import RedisClient
from app.config.logging import setup_logging
from app.config.settings import settings
from app.web.health import router as health_router

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Jefferson API",
    description="Warframe Discord bot web interface and health monitoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc" if settings.WEB_DEBUG else None,
)

app.include_router(health_router)

redis_client = RedisClient()


@app.get("/")
async def root():
    """Root endpoint with basic API info."""
    return {
        "service": "Jefferson API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": int(time.time()),
    }


@app.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Basic metrics endpoint.
    """
    try:
        client = redis_client.get_client()
        redis_info = client.info()

        metrics = {
            "service": "jefferson-api",
            "timestamp": int(time.time()),
            "redis": {
                "connected_clients": redis_info.get("connected_clients", 0),
                "used_memory_human": redis_info.get("used_memory_human", "0B"),
                "uptime_in_seconds": redis_info.get("uptime_in_seconds", 0),
                "total_commands_processed": redis_info.get(
                    "total_commands_processed", 0
                ),
            },
            "application": {
                "environment": "development" if settings.WEB_DEBUG else "production",
                "github_data_cached": bool(redis_client.get("github_data")),
                "wiki_data_cached": bool(redis_client.get("wiki_data")),
            },
        }

        return metrics

    except Exception as e:
        logger.error(f"Failed to collect metrics: {str(e)}")
        return {
            "service": "jefferson-api",
            "timestamp": int(time.time()),
            "error": str(e),
        }


@app.get("/cache-info")
async def cache_info() -> Dict[str, Any]:
    """
    Endpoint to check what data is currently cached.
    Useful for debugging and monitoring the job system.
    """
    try:
        cache_info = {"timestamp": int(time.time()), "cache_status": {}}

        # Check specific cache keys
        cache_keys = ["github_data", "wiki_data"]

        for key in cache_keys:
            try:
                client = redis_client.get_client()
                ttl = client.ttl(key)
                exists = client.exists(key)

                cache_info["cache_status"][key] = {
                    "exists": bool(exists),
                    "ttl_seconds": ttl if ttl > 0 else None,
                    "status": "active" if ttl > 0 else "expired/not_found",
                }
            except Exception as e:
                cache_info["cache_status"][key] = {
                    "exists": False,
                    "error": str(e),
                    "status": "check_failed",
                }

        return cache_info

    except Exception as e:
        logger.error(f"Failed to get cache info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "app.web.main:app",
        host=settings.WEB_HOST,
        port=settings.WEB_PORT,
        reload=settings.WEB_DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
