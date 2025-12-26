import aio_pika
import asyncio
from typing import Optional

class AsyncRabbitMQSingleton:
    _instance: Optional["AsyncRabbitMQSingleton"] = None
    _lock = asyncio.Lock()

    def __init__(self, connection: aio_pika.RobustConnection):
        self.connection = connection

    @classmethod
    async def get_instance(cls, cfg: dict) -> "AsyncRabbitMQSingleton":
        async with cls._lock:
            if cls._instance is None or cls._instance.connection.is_closed:
                # If instance exists but connection is closed, clear it
                if cls._instance:
                    try:
                        await cls._instance.close()
                    except:
                        pass
                
                connection = await aio_pika.connect_robust(
                    host=cfg["host"],
                    port=cfg["port"],
                    login=cfg["username"],
                    password=cfg["password"],
                    virtualhost=cfg.get("vhost", "/"),
                    heartbeat=30,
                )
                cls._instance = cls(connection)
        return cls._instance

    async def get_channel(self) -> aio_pika.RobustChannel:
        return await self.connection.channel()

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
