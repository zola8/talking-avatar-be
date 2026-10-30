import os


class Settings:
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))
    allowed_origins_raw: str = os.getenv("ALLOWED_ORIGINS",
                                         "http://localhost:5173,https://react-talking-avatar.zola8.workers.dev")
    azure_speech_region = "westeurope"
    azure_speech_key = os.getenv("AZURE_SPEECH_KEY", "")

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
