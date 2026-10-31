import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import azure
from api.routes import chat
from api.routes import main_route

logger = logging.getLogger(__name__)

_allowed_origins = [
    "http://localhost:5173",
    "https://react-talking-avatar.zola8.workers.dev",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Starting lifespan")
    yield
    logger.debug("Finishing lifespan")


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
        allow_origins=_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(main_route.router)
    app.include_router(chat.router)
    app.include_router(azure.router)

    return app
