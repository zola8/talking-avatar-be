import os

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root() -> dict:
    return {"status": "ok"}


@router.get("/debug-env")
def debug_env():
    return {
        "os.azure_speech_key": str(os.getenv("AZURE_SPEECH_KEY")),
    }
