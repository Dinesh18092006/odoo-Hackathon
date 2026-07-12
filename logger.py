"""Structured logger configuration."""
import logging
import sys
from config import settings


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    In development: logs to stdout with DEBUG level.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    return logger


# Application-wide logger
logger = get_logger("assetflow")
