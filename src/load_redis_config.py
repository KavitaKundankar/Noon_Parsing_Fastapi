import asyncio
import json
from config import REDIS_CFG
import config as default_config
from .redis_singleton import AsyncRedisSingleton
from .singleton import AsyncRabbitMQSingleton


from logger_config import logger

async def load_config_from_redis():
    """Fetch configuration from Redis keys."""
    redis_mgr = await AsyncRedisSingleton.get_instance(**REDIS_CFG)
    client = await redis_mgr.get_client()
    
    # 1. Load Rabbit Config (JSON string)
    # Expected Redis key: "RABBIT_CFG"
    rabbit_cfg_raw = await client.get("RABBIT_CFG")
    rabbit_cfg = json.loads(rabbit_cfg_raw) if rabbit_cfg_raw else default_config.RABBIT_CFG

    # 2. Load Queue Name
    # Expected Redis key: "RABBIT_QUEUE"
    queue_name = await client.get("RABBIT_QUEUE") or default_config.QUEUE_NAME

    # 3. Load Daily Limit
    # Expected Redis key: "RABBIT_LIMIT"
    limit_raw = await client.get("RABBIT_LIMIT")
    daily_limit = int(limit_raw) if limit_raw else default_config.DAILY_LIMIT

    return {
        "RABBIT_CFG": rabbit_cfg,
        "QUEUE_NAME": queue_name,
        "DAILY_LIMIT": daily_limit
    }

async def reconcile_worker_resources(current_cfg, limit_manager, rabbit, channel, queue):
    """
    Ensures configuration is up-to-date and connections are alive.
    Returns: (new_cfg, new_rabbit, new_channel, new_queue)
    """
    try:
        new_cfg = await load_config_from_redis()
        
        # Determine if we need to (re)initialize RabbitMQ
        needs_init = False
        if new_cfg != current_cfg:
            logger.info("⚙️ Configuration updated from Redis. (Re)initializing RabbitMQ...")
            needs_init = True
        elif rabbit is None or channel is None or queue is None:
            logger.info("⚙️ RabbitMQ resources are missing or stale. Initializing...")
            needs_init = True
        elif rabbit.connection.is_closed:
            logger.info("⚙️ RabbitMQ connection is closed. Reconnecting...")
            needs_init = True

        if needs_init:
            limit_manager.limit = new_cfg["DAILY_LIMIT"]
            
            if rabbit:
                try:
                    await rabbit.close()
                except:
                    pass

            rabbit = await AsyncRabbitMQSingleton.get_instance(new_cfg["RABBIT_CFG"])
            channel = await rabbit.get_channel()
            await channel.set_qos(prefetch_count=1)
            queue = await channel.declare_queue(new_cfg["QUEUE_NAME"], durable=True)
            return new_cfg, rabbit, channel, queue
        
        # If config hasn't changed and connection is healthy, verify Redis
        redis_mgr = await AsyncRedisSingleton.get_instance(**REDIS_CFG)
        if not await redis_mgr.ping():
            logger.warning("⚠️ Redis connection lost. Triggering re-init...")
            return None, None, None, None # Force re-init next iteration
            
        return current_cfg, rabbit, channel, queue

    except Exception as e:
        logger.error(f"⚠️ Resource reconciliation error: {e}. Retrying in 10s...")
        await asyncio.sleep(10)
        return None, None, None, None # Force re-init