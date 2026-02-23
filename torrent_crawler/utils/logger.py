import sys
import os
from loguru import logger as _logger

def setup_logger():
    """Sets up the global logger with rotation and custom formatting."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Remove default handler
    _logger.remove()

    # Add custom console handler with colors
    _logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )

    # Add file handler with rotation and compression
    _logger.add(
        os.path.join(log_dir, "app.log"),
        rotation="10 MB",
        retention="1 week",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )

    return _logger

# Initialize logger instance
logger = setup_logger()
