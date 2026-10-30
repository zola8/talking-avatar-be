from core.create_app import create_app
from core.logging_config import configure_logging

configure_logging()

app = create_app()

try:
    from workers import asgi

    Default = asgi.entrypoint(app)
except ModuleNotFoundError:
    pass

if __name__ == "__main__":
    import uvicorn

    print("Swagger UI: http://localhost:8080/docs")
    uvicorn.run(app, host="0.0.0.0", port=8080)
