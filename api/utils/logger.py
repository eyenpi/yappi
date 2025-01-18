import logging
import os
from logging.handlers import RotatingFileHandler

# Define log directory
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Create a rotating file handler (max size: 5MB per file, keep 3 backups)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
file_handler.setLevel(logging.INFO)

# Log format
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
file_handler.setFormatter(formatter)

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler],  # Logs to both file and console
)


# Function to get module-specific logger
def get_logger(module_name: str):
    return logging.getLogger(module_name)
