import asyncio
from datetime import datetime, timedelta
from logger_config import logger

class DailyLimitManager:
    def __init__(self, limit: int):
        self.limit = limit
        self.count = 0
        self.reset_time = None

    def _get_next_reset_time(self):
        """Calculate the next 1 AM reset time."""
        now = datetime.now()
        target = now.replace(hour=1, minute=0, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target

    async def check_and_wait(self):
        now = datetime.now()

        # If limit reached → sleep until next 1 AM
        if self.count >= self.limit:
            if not self.reset_time:
                self.reset_time = self._get_next_reset_time()
                logger.info(f"🛑 Daily limit of {self.limit} reached. Waiting until {self.reset_time}")

            wait_seconds = (self.reset_time - now).total_seconds()

            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)

            # Reset after the sleep period
            self.count = 0
            self.reset_time = None
            logger.info("✅ Daily reset period over. Counter cleared.")

    def increment(self):
        self.count += 1
        logger.info(f"📊 Progress: {self.count}/{self.limit}")
