from __future__ import annotations

import logging
import os

from utils.request_context import request_id_var


class _RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()  # type: ignore[attr-defined]
        return True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger with a console handler."""
    logger = logging.getLogger(name)
    level = getattr(logging, os.getenv("LOG_LEVEL", "DEBUG").upper(), logging.DEBUG)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | rid=%(request_id)s | %(message)s"
            )
        )
        handler.addFilter(_RequestIDFilter())
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger
