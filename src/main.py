import uvicorn
from dotenv import load_dotenv

from core.create_app import create_app
from core.logging_config import configure_logging

load_dotenv()

configure_logging()

if __name__ == "__main__":
    print("Swagger UI: http://localhost:8080/docs")
    uvicorn.run(create_app(), port=8080)
