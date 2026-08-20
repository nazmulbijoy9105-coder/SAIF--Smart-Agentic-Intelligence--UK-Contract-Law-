"""SAIF Structured Logging"""
import logging
import sys
from app.utils.config import get_settings

settings = get_settings()

logger = logging.getLogger("saif")
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
