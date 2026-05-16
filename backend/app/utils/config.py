from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from app.utils.logger import logger

class Settings(BaseSettings):
    APP_NAME: str = "SAIF"
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_MAX_TOKENS: int = 8192
    GEMINI_TEMPERATURE: float = 0.1
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_CURRENCY: str = "gbp"
    UPSTASH_REDIS_URL: str = ""
    UPSTASH_REDIS_TOKEN: str = ""
    RATE_LIMIT_REQUESTS: int = 20
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    TRUSTED_HOSTS: str = "localhost"
    
    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}

@lru_cache()
def get_settings() -> Settings:
    return Settings()
