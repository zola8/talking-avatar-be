import os

from fastapi import Request
from workers import asgi

from core.create_app import create_app
from core.logging_config import configure_logging

configure_logging()

_app = None


def apply_worker_env(env):
    if not env:
        return

    for key in ["AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION", "ALLOWED_ORIGINS"]:
        val = getattr(env, key, None)
        if val is not None:
            os.environ[key] = val


class Default(asgi.WorkerEntrypoint):
    def __init__(self, ctx, env):
        super().__init__(ctx, env)
        if env:
            apply_worker_env(env)

    async def fetch(self, request: Request, env, ctx):
        global _app
        if _app is None:
            _app = create_app()
        return await asgi.fetch(_app, request, env, ctx)
