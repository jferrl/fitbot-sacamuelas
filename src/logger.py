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
        # Use descriptive format to minimize GitHub secret redaction
        # Format: "Nov 01 at 12h06m24s CET"
        return dt.strftime("%b %d at %Hh%Mm%Ss %Z")

# Create handler with custom formatter
handler = logging.StreamHandler()
formatter = MadridTimeFormatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%b %d at %Hh%Mm%Ss %Z"
)
handler.setFormatter(formatter)

# Configure logger
logger = logging.getLogger("fitbot")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
