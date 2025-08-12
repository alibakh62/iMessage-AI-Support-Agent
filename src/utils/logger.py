"""
Logging configuration and utilities.
"""

import logging
import sys
from typing import Optional
from pathlib import Path

from ..config import get_settings


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        format_string: Custom log format string (optional)

    Returns:
        Configured logger instance
    """

    # Get settings
    settings = get_settings()

    # Set default values
    log_level = level or settings.log_level
    log_format = format_string or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()), format=log_format, handlers=[]
    )

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)

    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)

        logging.getLogger().addHandler(file_handler)

    # Add console handler
    logging.getLogger().addHandler(console_handler)

    # Create and return logger
    logger = logging.getLogger("imessage_ai_agent")
    logger.setLevel(getattr(logging, log_level.upper()))

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_function_call(func_name: str, **kwargs):
    """
    Decorator to log function calls with parameters.

    Args:
        func_name: Name of the function being called
        **kwargs: Function parameters to log
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger("function_calls")
            logger.info(f"Calling {func_name} with args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"{func_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func_name} failed with error: {e}")
                raise

        return wrapper

    return decorator
