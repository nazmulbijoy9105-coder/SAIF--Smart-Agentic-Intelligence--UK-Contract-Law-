"""
SAIF Configuration — Validated at startup
Creator: Md Nazmul Islam (Bijoy) | NB TECH
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from app.utils.logger import logger


class Settings(BaseSettings):
    APP_NAME: str = "SAIF"
    ENVIRONMENT: str = Field(
        default="development",
        pattern="^(development|staging|production)$",
    )
    DEBUG: bool = False

    # Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_MAX_TOKENS: int = 8192
    GEMINI_TEMPERATURE: float = 0.1

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_CURRENCY: str = "gbp"

    # Redis
    UPSTASH_REDIS_URL: str = ""
    UPSTASH_REDIS_TOKEN: str = ""
    RATE_LIMIT_REQUESTS: int = 20
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Security
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    TRUSTED_HOSTS: str = "localhost"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def allowed_origins_list(self) -> list:
        """Parse ALLOWED_ORIGINS into a clean list."""
        origins = []
        for o in self.ALLOWED_ORIGINS.split(","):
            o = o.strip()
            if o:
                origins.append(o)
        # Always include localhost for development
        if "http://localhost:3000" not in origins:
            origins.append("http://localhost:3000")
        return origins


@lru_cache()
def get_settings() -> Settings:
    try:
        s = Settings()
        logger.info(f"✅ Config loaded — ENV={s.ENVIRONMENT}")
        return s
    except Exception as e:
        logger.critical(f"❌ CONFIG FAILED: {e}")
        raise SystemExit(1)
