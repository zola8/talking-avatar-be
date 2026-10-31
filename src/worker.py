from fastapi import Request
from workers import asgi

from core.create_app import create_app
from core.logging_config import configure_logging

configure_logging()

_app = None


class Default(asgi.WorkerEntrypoint):
    def __init__(self, ctx, env):
        super().__init__(ctx, env)

    async def fetch(self, request: Request, env, ctx):
        global _app
        if _app is None:
            _app = create_app()
        return await asgi.fetch(_app, request, env, ctx)
