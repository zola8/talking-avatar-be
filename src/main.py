from fastapi import Request
from workers import asgi

from core.config import apply_worker_env
from core.config import settings
from core.create_app import create_app
from core.logging_config import configure_logging

configure_logging()
app = create_app()


class Default(asgi.WorkerEntrypoint):
    def __init__(self, ctx, env):
        super().__init__(ctx, env)
        if env:
            apply_worker_env(env)
            print(f"Initialized settings with Azure Region: {settings.azure_speech_region}")

    async def fetch(self, request: Request, env, ctx):
        return await asgi.fetch(app, request, env, ctx)


if __name__ == "__main__":
    import uvicorn

    print("Swagger UI: http://localhost:8080/docs")
    uvicorn.run(app, host="0.0.0.0", port=8080)
