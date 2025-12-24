import redis.asyncio as redis
import asyncio
from typing import Optional

class AsyncRedisSingleton:
    _instance: Optional["AsyncRedisSingleton"] = None
    _lock = asyncio.Lock()

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, username: str = None, password: str = None):
        self.redis = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            username=username, 
            password=password, 
            decode_responses=True
        )

    @classmethod
    async def get_instance(cls, host: str = "localhost", port: int = 6379, db: int = 0, username: str = None, password: str = None) -> "AsyncRedisSingleton":
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls(host=host, port=port, db=db, username=username, password=password)
        return cls._instance

    async def get_client(self) -> redis.Redis:
        return self.redis

    async def ping(self) -> bool:
        """Check if the Redis connection is alive."""
        try:
            return await self.redis.ping()
        except Exception:
            return False

    async def close(self):
        if self.redis:
            await self.redis.close()
