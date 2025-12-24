import asyncio
from .daily_limit import DailyLimitManager
from .load_redis_config import load_config_from_redis, reconcile_worker_resources
from config import REDIS_CFG
import config as default_config

# Shared state
limit_manager = DailyLimitManager(limit=default_config.DAILY_LIMIT)


async def rabbit_worker():
    """Background task that consumes messages from RabbitMQ."""
    print("🚀 Starting RabbitMQ Worker (Clean Refactored Mode)...")
    
    rabbit = None
    channel = None
    queue = None
    current_cfg = None

    while True:
        try:
            # 1. Handle daily sleep/cooldown
            await limit_manager.check_and_wait()

            # 2. Reconcile settings and connections (Redis + RabbitMQ)
            current_cfg, rabbit, channel, queue = await reconcile_worker_resources(
                current_cfg, limit_manager, rabbit, channel, queue
            )

            # 3. If reconciliation failed (e.g. Redis/Rabbit down), wait and retry
            if not queue:
                continue

            # 4. Pull and process message
            message = await queue.get(fail=False)

            if message:
                async with message.process(requeue=True):
                    body = message.body.decode()
                    print(f"📩 Processing message (length: {len(body)})...")
                    await asyncio.sleep(1) 

                print("✅ Message ACKed.")
                limit_manager.increment()
            else:
                # Idle wait if queue is empty
                await asyncio.sleep(5)

        except asyncio.CancelledError:
            print("🛑 Worker task cancelled.")
            break
        except Exception as e:
            print(f"❌ Worker loop error: {e}")
            current_cfg = None # Reset to trigger full recovery
            await asyncio.sleep(10)
