import logging
import os
from datetime import datetime

# Define logs directory at project root (outside src)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Create logs directory if it doesn't exist
os.makedirs(LOGS_DIR, exist_ok=True)

# Define log file name with current date
LOG_FILE = os.path.join(LOGS_DIR, f"{datetime.now().strftime('%Y%m%d')}.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Set external library levels
logging.getLogger("pika").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.INFO)

logger = logging.getLogger("noon_report_worker")
logger.info("*** Logging system initialized ***")
