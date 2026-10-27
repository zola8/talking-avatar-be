import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))

    allowed_origins_raw: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")

    @property
    def allowed_origins(self) -> list[str]:
        """Parse the comma-separated origins string into a list."""
        if not self.allowed_origins_raw:
            return ["*"]
        return [
            origin.strip()
            for origin in self.allowed_origins_raw.split(",")
            if origin.strip()
        ]


settings = Settings()
