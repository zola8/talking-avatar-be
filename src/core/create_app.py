import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import azure
from api.routes import chat
from api.routes import main_route
from core.config import settings
from core.dependencies import close_http_clients

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Starting lifespan")
    yield
    logger.debug("Finishing lifespan")
    await close_http_clients()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Avatar Backend",
        description="Backend API for the React Talking Avatar app",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(main_route.router)
    app.include_router(chat.router)
    app.include_router(azure.router)

    return app
