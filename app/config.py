import os
import logging
import sys
from dotenv import load_dotenv

load_dotenv(".env")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

MODEL_NAME = "gemini-3.1-flash-lite-preview"

MLFLOW_TRACKING_URI = "http://localhost:5000"


# ========================================
# Logging Configuration
# ========================================

def configure_logging():
    """
    Configure comprehensive logging for the application.
    Logs to both console and file for debugging.
    """
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s"
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Console handler (INFO level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (DEBUG level)
    file_handler = logging.FileHandler("debug.log", mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Set specific loggers
    logging.getLogger("app.research").setLevel(logging.DEBUG)
    logging.getLogger("app.agents").setLevel(logging.DEBUG)
    logging.getLogger("app.llm").setLevel(logging.INFO)
    
    root_logger.info("=" * 80)
    root_logger.info("Application Logging Initialized")
    root_logger.info("=" * 80)


# Initialize logging on module import
configure_logging()