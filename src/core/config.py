import os
from dataclasses import dataclass
from dataclasses import field


@dataclass
class Settings:
    """Application settings.

    Initialized once at module import time. Reads from:
      1. Local `.env` file (via python-dotenv) — local dev only
      2. `os.environ` — populated by _bootstrap_worker_env() on Cloudflare,
         or by your shell/.env locally
    """
    allowed_origins: list[str] = field(default_factory=lambda: [
        "http://localhost:5173",
        "https://react-talking-avatar.zola8.workers.dev",
    ])
    azure_speech_region: str = "westeurope"
    azure_speech_key: str = ""

    def __post_init__(self) -> None:
        raw = os.getenv("ALLOWED_ORIGINS", "")
        if raw:
            self.allowed_origins = _parse_origins(raw)
        self.azure_speech_region = os.getenv(
            "AZURE_SPEECH_REGION", self.azure_speech_region
        )
        self.azure_speech_key = os.getenv("AZURE_SPEECH_KEY", "")


def _parse_origins(raw: str) -> list[str]:
    return [o.strip() for o in raw.split(",") if o.strip()]


def _bootstrap_worker_env() -> None:
    try:
        from js import cloudflare        # type: ignore[import-not-found]
        env = cloudflare.workers.env
    except Exception:
        _load_dotenv_if_present()
        return

    for key in dir(env):
        if key.startswith("_"):
            continue
        try:
            value = getattr(env, key)
        except Exception:
            continue
        if isinstance(value, str):
            os.environ[key] = value


def _load_dotenv_if_present() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass


# Bootstrap BEFORE constructing the singleton
_bootstrap_worker_env()

# Module-level singleton — Settings instance initialized once at startup.
settings = Settings()
