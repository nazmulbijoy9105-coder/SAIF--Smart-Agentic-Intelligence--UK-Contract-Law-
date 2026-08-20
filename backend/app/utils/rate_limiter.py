"""SAIF In-Memory Rate Limiter (Sliding Window)
Production deployments should replace this with Redis-backed limiter.
"""
import time
from collections import defaultdict, deque
from typing import Dict, Tuple
from app.utils.config import get_settings
from app.utils.logger import logger

settings = get_settings()

class RateLimiter:
    def __init__(self):
        self._windows: Dict[str, deque] = defaultdict(deque)
        self.max_requests = settings.RATE_LIMIT_REQUESTS
        self.window = settings.RATE_LIMIT_WINDOW

    def is_allowed(self, key: str) -> Tuple[bool, int]:
        now = time.time()
        window = self._windows[key]
        # Remove expired timestamps
        while window and window[0] < now - self.window:
            window.popleft()
        if len(window) >= self.max_requests:
            retry_after = int(window[0] + self.window - now) + 1
            return False, retry_after
        window.append(now)
        return True, 0

rate_limiter = RateLimiter()
 
