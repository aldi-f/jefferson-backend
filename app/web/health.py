import logging
import time
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.clients.redis.client import RedisClient
from app.config.settings import settings

router = APIRouter(prefix="/health", tags=["health"])
logger = logging.getLogger(__name__)

redis_client = RedisClient()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    health_status = {"status": "healthy", "timestamp": int(time.time()), "checks": {}}

    overall_healthy = True

    # Check Redis connection
    try:
        client = redis_client.get_client()
        client.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "response_time": "< 1ms",
            "details": {
                "host": settings.REDIS_HOST,
                "port": settings.REDIS_PORT,
                "db": settings.REDIS_DB,
            },
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e),
            "details": {
                "host": settings.REDIS_HOST,
                "port": settings.REDIS_PORT,
                "db": settings.REDIS_DB,
            },
        }
        overall_healthy = False

    # Check GitHub data cache
    try:
        github_data = redis_client.get("github_data")
        if github_data:
            health_status["checks"]["github_data"] = {
                "status": "healthy",
                "cached": True,
                "details": "GitHub data is cached and available",
            }
        else:
            health_status["checks"]["github_data"] = {
                "status": "warning",
                "cached": None,
                "details": "GitHub data not cached - job may need to run",
            }
    except Exception as e:
        health_status["checks"]["github_data"] = {
            "status": "unhealthy",
            "error": str(e),
            "details": "Failed to check GitHub data cache",
        }
        overall_healthy = False

    # Check Wiki data cache
    try:
        wiki_data = redis_client.get("wiki_data")
        if wiki_data:
            health_status["checks"]["wiki_data"] = {
                "status": "healthy",
                "cached": True,
                "details": "Wiki data is cached and available",
            }
        else:
            health_status["checks"]["wiki_data"] = {
                "status": "warning",
                "cached": None,
                "details": "Wiki data not cached - job may need to run",
            }
    except Exception as e:
        health_status["checks"]["wiki_data"] = {
            "status": "unhealthy",
            "error": str(e),
            "details": "Failed to check Wiki data cache",
        }
        overall_healthy = False

    # Check Worldstate API
    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.head(settings.WORLDSTATE_URL, timeout=5) as response:
                if response.status < 500:
                    health_status["checks"]["worldstate_api"] = {
                        "status": "healthy",
                        "response_time": f"{response.status} response code",
                        "details": "Worldstate API is reachable",
                    }
                else:
                    health_status["checks"]["worldstate_api"] = {
                        "status": "degraded",
                        "response_code": response.status,
                        "details": "Worldstate API responding with errors",
                    }
                    overall_healthy = False
    except Exception as e:
        health_status["checks"]["worldstate_api"] = {
            "status": "unhealthy",
            "error": str(e),
            "details": "Could not reach Worldstate API",
        }
        overall_healthy = False

    health_status["status"] = "healthy" if overall_healthy else "unhealthy"

    return health_status


@router.get("/simple")
async def simple_health_check() -> Dict[str, str]:
    """
    Health check endpoint for load balancers.
    """
    try:
        client = redis_client.get_client()
        client.ping()
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="Service unhealthy")
