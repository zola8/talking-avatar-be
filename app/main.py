import uvicorn

from app.core.create_app import create_app
from app.core.logging_config import configure_logging

configure_logging()

app = create_app()

if __name__ == '__main__':
    print("http://localhost:8080/docs")
    uvicorn.run(app, port=8080)
