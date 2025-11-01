import logging
from datetime import datetime
from zoneinfo import ZoneInfo
import time

# Custom formatter that uses Madrid timezone
class MadridTimeFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, timezone="Europe/Madrid"):
        super().__init__(fmt, datefmt)
        self.timezone = ZoneInfo(timezone)
    
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=self.timezone)
        if datefmt:
            return dt.strftime(datefmt)
        # Use letters instead of pure numbers to avoid GitHub secret redaction
        return dt.strftime("%Y-%b-%d %H:%M:%S %Z")  # e.g., 2025-Nov-01 10:00:00 CET

# Create handler with custom formatter
handler = logging.StreamHandler()
formatter = MadridTimeFormatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%b-%d %H:%M:%S %Z"
)
handler.setFormatter(formatter)

# Configure logger
logger = logging.getLogger("fitbot")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
