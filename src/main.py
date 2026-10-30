from core.create_app import create_app
from core.logging_config import configure_logging

configure_logging()

app = create_app()

# Register the Workers entrypoint only when running on Pyodide.
# Locally (uvicorn) the `workers` module can't import `js`, so we skip it.
try:
    from workers import asgi

    Default = asgi.entrypoint(app)
except ModuleNotFoundError:
    pass

if __name__ == '__main__':
    import uvicorn

    print("http://localhost:8080/docs")
    uvicorn.run(app, port=8080)
