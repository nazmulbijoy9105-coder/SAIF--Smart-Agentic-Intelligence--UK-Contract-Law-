"""
SAIF Rate Limiter — Redis-backed
Creator: Md Nazmul Islam (Bijoy) | NB TECH
"""
from app.utils.config import get_settings
from app.utils.logger import logger


class RateLimiter:
    """Rate limiter with graceful Redis fallback."""

    def __init__(self):
        self._client = None
        self._initialized = False

    def _ensure_init(self):
        if self._initialized:
            return
        settings = get_settings()
        if settings.UPSTASH_REDIS_URL:
            try:
                import redis as redis_lib
                self._client = redis_lib.from_url(
                    settings.UPSTASH_REDIS_URL,
                    password=settings.UPSTASH_REDIS_TOKEN or None,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )
                self._client.ping()
                logger.info("✅ Redis rate limiter connected")
            except Exception as e:
                logger.warning(f"⚠️ Redis unavailable, rate limiting disabled: {e}")
                self._client = None
        else:
            logger.warning("⚠️ No REDIS_URL — rate limiting disabled")
        self._initialized = True

    def is_rate_limited(self, client_id: str) -> bool:
        """Returns True if rate limited (should block)."""
        self._ensure_init()
        if not self._client:
            return False

        settings = get_settings()
        key = f"saif:ratelimit:{client_id}"

        try:
            current = self._client.get(key)
            if current and int(current) >= settings.RATE_LIMIT_REQUESTS:
                return True

            pipe = self._client.pipeline()
            pipe.incr(key)
            pipe.expire(key, settings.RATE_LIMIT_WINDOW_SECONDS)
            pipe.execute()
            return False

        except Exception as e:
            logger.error(f"Redis error (allowing request): {e}")
            return False


rate_limiter = RateLimiter()
