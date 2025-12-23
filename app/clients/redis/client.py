from typing_extensions import Self
from typing import Optional

import redis
from app.config.settings import settings


class RedisClient:
    """Redis client with singleton pattern."""
    
    _instance: Self | None = None
    
    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
            cls._instance._connected = False
        return cls._instance
    
    def __init__(self):
        if not self._connected:
            self._connect()
    
    def _connect(self) -> None:
        """Establish Redis connection."""
        try:
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self._client.ping()
            self._connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")
    
    def get_client(self):
        """Get Redis client instance."""
        if not self._connected or not self._client:
            self._connect()
        return self._client
    
    def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        try:
            client = self.get_client()
            return client.get(key)
        except Exception as e:
            print(f"Redis get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration."""
        try:
            client = self.get_client()
            return bool(client.set(key, value, ex=ex))
        except Exception as e:
            print(f"Redis set error for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            client = self.get_client()
            return bool(client.exists(key))
        except Exception as e:
            print(f"Redis exists error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            client = self.get_client()
            return bool(client.delete(key))
        except Exception as e:
            print(f"Redis delete error for key {key}: {e}")
            return False
    
    def ping(self) -> bool:
        """Ping Redis to check connection."""
        try:
            client = self.get_client()
            return client.ping()
        except Exception as e:
            print(f"Redis ping error: {e}")
            return False
    
    def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            self._client.close()
            self._connected = False


# Export singleton instance
redis_client = RedisClient()