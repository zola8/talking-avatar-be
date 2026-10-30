from core.config import Settings
from core.config import _parse_origins
from core.create_app import create_app
from core.logging_config import configure_logging

configure_logging()



# Module-level bootstrap — works for local dev (loads .env).
# On Workers, this also runs but with empty env; gets overridden in Default.__init__.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Build a default Settings + app for local uvicorn.
# On Workers these get replaced when Default is instantiated.
settings = Settings()
app = create_app()


try:
    from workers import WorkerEntrypoint, asgi

    class Default(WorkerEntrypoint):
        """Cloudflare Workers entrypoint.

        `__init__` runs once per isolate (cold start). We populate the
        Settings singleton from `self.env` here, then build the FastAPI
        app so middleware (CORS) picks up the real origins.
        """
        def __init__(self, ctx=None, env=None):
            # `self.env` is automatically set by WorkerEntrypoint before
            # this method runs (when called by the runtime). When called
            # manually (e.g. by the ASGI adapter), `env` is passed in.
            super().__init__(ctx, env)  # type: ignore[misc]

            env_obj = getattr(self, "env", None) or env
            if env_obj is not None:
                # Populate settings from real Cloudflare env binding
                settings = Settings(
                    azure_speech_key=getattr(env_obj, "AZURE_SPEECH_KEY", "") or "",
                    azure_speech_region=getattr(
                        env_obj, "AZURE_SPEECH_REGION", "westeurope"
                    ),
                    allowed_origins=(
                        _parse_origins(getattr(env_obj, "ALLOWED_ORIGINS", "") or "")
                        or Settings().allowed_origins
                    ),
                )

            # Build FastAPI app with the now-populated settings
            # (so CORS middleware captures real origins, etc.)
            self._app = create_app()

            # Cache the ASGI handler instance (built once per isolate)
            AsgiHandler = asgi.entrypoint(self._app)
            self._asgi_handler = AsgiHandler() if isinstance(AsgiHandler, type) else AsgiHandler

        async def fetch(self, request, env=None, ctx=None):
            # Delegate to the ASGI handler — it knows how to bridge
            # Workers requests ↔ ASGI (FastAPI).
            return await self._asgi_handler.fetch(request, env, ctx)

except ModuleNotFoundError:
    # Local dev — `workers` module isn't available on CPython.
    # `app` above is what uvicorn serves.
    pass


if __name__ == "__main__":
    import uvicorn

    print("Swagger UI: http://localhost:8080/docs")
    uvicorn.run(app, host="0.0.0.0", port=8080)
