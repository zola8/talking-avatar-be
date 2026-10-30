import os
from dataclasses import dataclass
from dataclasses import field


@dataclass
class Settings:
    allowed_origins: list[str] = field(default_factory=lambda: [
        "http://localhost:5173",
        "https://react-talking-avatar.zola8.workers.dev",
    ])
    azure_speech_region: str = "westeurope"
    azure_speech_key: str = ""

    @classmethod
    def from_env(cls, worker_env=None) -> "Settings":
        """Build Settings.

        - On Workers: pass the `env` from your fetch handler → reads Cloudflare bindings.
        - Locally: pass None → loads `.env` via python-dotenv, then reads os.environ.
        """
        if worker_env is not None:
            raw_origins = getattr(worker_env, "ALLOWED_ORIGINS", "")
            origins = (
                _parse_origins(raw_origins)
                if raw_origins
                else cls().allowed_origins
            )
            return cls(
                allowed_origins=origins,
                azure_speech_region=getattr(
                    worker_env, "AZURE_SPEECH_REGION", "westeurope"
                ),
                azure_speech_key=getattr(worker_env, "AZURE_SPEECH_KEY", ""),
            )

        _load_dotenv_if_present()

        raw_origins = os.getenv("ALLOWED_ORIGINS", "")
        origins = (
            _parse_origins(raw_origins)
            if raw_origins
            else cls().allowed_origins
        )
        return cls(
            allowed_origins=origins,
            azure_speech_region=os.getenv("AZURE_SPEECH_REGION", "westeurope"),
            azure_speech_key=os.getenv("AZURE_SPEECH_KEY", ""),
        )


def _parse_origins(raw: str) -> list[str]:
    return [o.strip() for o in raw.split(",") if o.strip()]


def _load_dotenv_if_present() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass


settings = Settings.from_env()
