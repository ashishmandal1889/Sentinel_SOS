"""
Sentinel SOS - Logging Module.

Configures structured logging across the application, formatting log output
cleanly for both local development and containerized production environments.
"""

import logging
import sys
from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configures root and sentinel loggers based on environment profile."""
    log_level = logging.DEBUG if settings.SENTINEL_DEBUG or settings.is_development else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger("sentinel")
    logger.setLevel(log_level)
    logger.handlers = [handler]
    logger.propagate = False

    # Quieten third-party noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return logger


logger = setup_logging()
