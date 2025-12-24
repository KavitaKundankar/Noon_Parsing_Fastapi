# import asyncio
# from datetime import datetime, timedelta

# class DailyLimitManager:
#     def __init__(self, limit: int):
#         self.limit = limit
#         self.count = 0
#         self.reset_time = self._get_next_reset_time()

#     def _get_next_reset_time(self):
#         now = datetime.now()
#         return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

#     async def check_and_wait(self):
#         now = datetime.now()
#         if now >= self.reset_time:
#             self.count = 0
#             # self.reset_time = self._get_next_reset_time()
#             self.reset_time = now.replace(hour=0, minute=5, second=0, microsecond=0)

#         if self.count >= self.limit:
#             wait_seconds = (self.reset_time - now).total_seconds()
#             print(f"🛑 Daily limit of {self.limit} reached. Waiting for next day...")
#             await asyncio.sleep(wait_seconds)
#             self.count = 0
#             self.reset_time = self._get_next_reset_time()

#     def increment(self):
#         self.count += 1
#         print(f"📊 Progress: {self.count}/{self.limit}")


import asyncio
from datetime import datetime, timedelta


class DailyLimitManager:
    def __init__(self, limit: int, cooldown_minutes: int = 5):
        self.limit = limit
        self.cooldown = timedelta(minutes=cooldown_minutes)
        self.count = 0
        self.reset_time = None

    async def check_and_wait(self):
        now = datetime.now()

        # If limit reached → start cooldown
        if self.count >= self.limit:
            if not self.reset_time:
                self.reset_time = now + self.cooldown
                print(
                    f" Limit {self.limit} reached. "
                    f"Cooling down until {self.reset_time.strftime('%H:%M:%S')}"
                )

            wait_seconds = (self.reset_time - now).total_seconds()

            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)

            # Reset after cooldown
            self.count = 0
            self.reset_time = None
            print("✅ Cooldown over. Counter reset.")

    def increment(self):
        self.count += 1
        print(f"📊 Progress: {self.count}/{self.limit}")
