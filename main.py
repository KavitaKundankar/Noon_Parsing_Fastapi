import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.worker import rabbit_worker, limit_manager
from src.singleton import AsyncRabbitMQSingleton
from src.redis_singleton import AsyncRedisSingleton
from config import REDIS_CFG

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Open Redis & RabbitMQ, start worker
    redis_mgr = await AsyncRedisSingleton.get_instance(**REDIS_CFG)
    worker_task = asyncio.create_task(rabbit_worker())
    
    yield
    
    # Shutdown: Clean up all connections
    worker_task.cancel()
    
    # Close RabbitMQ
    # (Since we don't have RABBIT_CFG here easily, 
    # we rely on the singleton's existing connection)
    if AsyncRabbitMQSingleton._instance:
        await AsyncRabbitMQSingleton._instance.close()
    
    # Close Redis
    await redis_mgr.close()
    
    print("👋 Microservice shutdown complete.")

app = FastAPI(title="Redis-Configured RabbitMQ Microservice", lifespan=lifespan)

@app.get("/status")
async def get_status():
    """Monitor state and current config."""
    if limit_manager is None:
        return {"status": "Worker not initialized yet"}
        
    return {
        "daily_count": limit_manager.count,
        "daily_limit": limit_manager.limit,
        "reset_time": limit_manager.reset_time,
        "status": "Running",
        "config_source": "Redis"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
