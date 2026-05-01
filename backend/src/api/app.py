from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.middleware.request_id import RequestIDMiddleware
from api.routes.chat import router as chat_router
from api.routes.health import router as health_router
from config import get_settings

app = FastAPI(title="Customer Service Agent")

app.add_middleware(RequestIDMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    if any(e.get("type") == "json_invalid" for e in errors):
        message = "Request body contains invalid JSON. Check for unescaped characters such as quotes."
    else:
        missing = [
            " → ".join(str(p) for p in e["loc"])
            for e in errors
            if e.get("type") == "missing"
        ]
        if missing:
            message = f"Missing required field(s): {', '.join(missing)}."
        else:
            message = "Invalid request. Check the request body and try again."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"error": message}
    )


settings = get_settings()
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(chat_router, prefix=settings.api_prefix)
