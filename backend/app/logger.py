import logging
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Log level mapping
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

# Formatter
# [2024-04-09 14:15:00] [INFO] [main.py:34] - My message
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(name: str):
    """Setup and return a logger instance."""
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if setup_logger is called multiple times for the same name
    if not logger.handlers:
        logger.setLevel(LOG_LEVEL)
        
        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        logger.addHandler(handler)
        
        # Optional: File handler
        # log_file = os.path.join(os.path.dirname(__file__), "..", "backend.log")
        # file_handler = logging.FileHandler(log_file, encoding='utf-8')
        # file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        # logger.addHandler(file_handler)

    return logger

# Default logger for general use
logger = setup_logger("backend")
