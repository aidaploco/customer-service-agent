from functools import lru_cache

from phoenix.otel import register

from config import get_settings
from utils.logger import get_logger

_logger = get_logger(__name__)


@lru_cache(maxsize=1)
def setup_tracing() -> None:
    """Configure Phoenix OTEL tracing. No-ops if PHOENIX_COLLECTOR_ENDPOINT is not set."""
    settings = get_settings()
    if not settings.phoenix_collector_endpoint:
        _logger.info("Phoenix tracing disabled — PHOENIX_COLLECTOR_ENDPOINT not set")
        return
    register(
        endpoint=settings.phoenix_collector_endpoint,
        project_name="customer-service-agent",
        auto_instrument=True,
    )
    _logger.info("Phoenix tracing enabled → %s", settings.phoenix_collector_endpoint)
