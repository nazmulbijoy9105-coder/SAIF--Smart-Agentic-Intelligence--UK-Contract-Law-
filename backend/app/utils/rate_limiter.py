import redis as redis_lib
from app.utils.config import get_settings
from app.utils.logger import logger

class RateLimiter:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
            try:
                s = get_settings()
                if s.UPSTASH_REDIS_URL:
                    cls._instance._client = redis_lib.from_url(s.UPSTASH_REDIS_URL, password=s.UPSTASH_REDIS_TOKEN or None, decode_responses=True, socket_connect_timeout=5)
                    cls._instance._client.ping()
            except Exception as e:
                logger.warning(f"Redis unavailable: {e}")
                cls._instance._client = None
        return cls._instance

    def is_rate_limited(self, client_id: str) -> bool:
        if not self._client: return False
        s = get_settings()
        key = f"saif:ratelimit:{client_id}"
        try:
            current = self._client.get(key)
            if current and int(current) >= s.RATE_LIMIT_REQUESTS: return True
            pipe = self._client.pipeline()
            pipe.incr(key)
            pipe.expire(key, s.RATE_LIMIT_WINDOW_SECONDS)
            pipe.execute()
            return False
        except Exception: return False

rate_limiter = RateLimiter()
