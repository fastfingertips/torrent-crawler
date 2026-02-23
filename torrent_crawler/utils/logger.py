import sys
import os
import logging
from loguru import logger as _logger

class InterceptHandler(logging.Handler):
    """
    Default handler from loguru documentation for intercepting standard logging messages.
    """
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = _logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        _logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

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

    # Intercept standard logging from libraries like requests, urllib3
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    return _logger

# Initialize logger instance
logger = setup_logger()
