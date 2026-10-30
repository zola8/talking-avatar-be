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


def _parse_origins(raw: str) -> list[str]:
    return [o.strip() for o in raw.split(",") if o.strip()]


try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

settings = Settings(
    azure_speech_key=os.getenv("AZURE_SPEECH_KEY", ""),
    azure_speech_region=os.getenv("AZURE_SPEECH_REGION", "westeurope"),
    allowed_origins=_parse_origins(os.getenv("ALLOWED_ORIGINS", "")) or [
        "http://localhost:5173",
        "https://react-talking-avatar.zola8.workers.dev",
    ],
)


def apply_worker_env(env):
    if not env:
        return

    for key in ["AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION", "ALLOWED_ORIGINS"]:
        val = getattr(env, key, None)
        if val is not None:
            if key == "AZURE_SPEECH_KEY":
                settings.azure_speech_key = val
            elif key == "AZURE_SPEECH_REGION":
                settings.azure_speech_region = val
            elif key == "ALLOWED_ORIGINS":
                parsed = _parse_origins(val)
                if parsed:
                    settings.allowed_origins = parsed
            if isinstance(val, str):
                os.environ[key] = val
