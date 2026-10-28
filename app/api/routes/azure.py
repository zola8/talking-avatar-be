import httpx
from fastapi import APIRouter
from fastapi import HTTPException

from app.core.config import settings

router = APIRouter(prefix="/azure", tags=["azure"])


@router.post("/token")
async def get_azure_token() -> str:
    if not settings.azure_speech_key:
        raise HTTPException(
            status_code=500,
            detail="AZURE_SPEECH_KEY not configured on the server",
        )

    url = f"https://{settings.azure_speech_region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers={"Ocp-Apim-Subscription-Key": settings.azure_speech_key},
            )
    except httpx.HTTPError as err:
        raise HTTPException(status_code=502, detail=f"Azure unreachable: {err}")

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Azure token exchange failed: {resp.text}",
        )

    return resp.text
