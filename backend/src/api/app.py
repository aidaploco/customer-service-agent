from fastapi import FastAPI

from api.middleware.request_id import RequestIDMiddleware
from api.routes.chat import router as chat_router
from api.routes.health import router as health_router
from config import get_settings

app = FastAPI(title="Customer Service Agent")

app.add_middleware(RequestIDMiddleware)

settings = get_settings()
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(chat_router, prefix=settings.api_prefix)
