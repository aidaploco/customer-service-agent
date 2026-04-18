from __future__ import annotations

import logging
import os


def get_logger(name: str) -> logging.Logger:
    """Return a named logger with a console handler."""
    logger = logging.getLogger(name)
    level = getattr(logging, os.getenv("LOG_LEVEL", "DEBUG").upper(), logging.DEBUG)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
        )
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger
