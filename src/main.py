import core.config as config_module
from core.config import Settings
from core.create_app import create_app
from core.logging_config import configure_logging

configure_logging()

app = create_app()

try:
    from workers import asgi

    AsgiHandler = asgi.entrypoint(app)


    class Default(AsgiHandler):
        async def fetch(self, request, env, ctx):
            config_module.settings = Settings.from_env(env)
            return await super().fetch(request, env, ctx)


except ModuleNotFoundError:
    # Local dev — `workers` module isn't available on CPython.
    pass

if __name__ == "__main__":
    import uvicorn

    print("Swagger UI: http://localhost:8080/docs")
    uvicorn.run(app, host="0.0.0.0", port=8080)
