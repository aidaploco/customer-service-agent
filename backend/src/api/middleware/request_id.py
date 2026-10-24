import re
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from utils.request_context import request_id_var

REQUEST_ID_HEADER = "X-Request-ID"
_VALID_REQUEST_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attaches a unique request ID to every request and echoes it in the response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Reuse a well-formed incoming X-Request-ID, otherwise generate a new UUID."""
        incoming = request.headers.get(REQUEST_ID_HEADER, "")
        request_id = (
            incoming if _VALID_REQUEST_ID.fullmatch(incoming) else str(uuid.uuid4())
        )
        request.state.request_id = request_id
        request_id_var.set(request_id)
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
