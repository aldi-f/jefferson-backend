import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from app.config.settings import settings


def setup_logging(level: Optional[str] = None) -> None:
    """Setup application logging with console and file handlers."""
    
    log_level = level or settings.LOG_LEVEL
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if LOG_FILE is specified)
    if settings.LOG_FILE:
        file_handler = RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)


# Legacy function for backward compatibility
def configure_logging(level: str = "INFO"):
    """Legacy function - use setup_logging() instead."""
    setup_logging(level)
