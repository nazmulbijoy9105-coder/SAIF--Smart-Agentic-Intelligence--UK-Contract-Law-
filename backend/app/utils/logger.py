import logging, sys
from datetime import datetime, timezone

class SAIFFormatter(logging.Formatter):
    def format(self, record):
        ts = datetime.now(timezone.utc).isoformat()
        return f"[{ts}] [{record.levelname}] [SAIF:{record.module}] {record.getMessage()}"

logger = logging.getLogger("saif")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(SAIFFormatter())
    logger.addHandler(handler)
logger.propagate = False
