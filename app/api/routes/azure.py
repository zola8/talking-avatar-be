import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.core.azure.errors import AzureConfigError
from app.core.azure.errors import AzureTokenError
from app.core.azure.errors import AzureUnavailableError
from app.core.azure.service import AzureService
from app.core.dependencies import get_azure_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/azure", tags=["azure"])


@router.post("/token")
async def get_azure_token(
    svc: AzureService = Depends(get_azure_service),
) -> str:
    logger.info("POST /azure/token")
    try:
        return await svc.issue_token()
    except AzureConfigError as err:
        # Server misconfigure - 500.
        raise HTTPException(status_code=500, detail=str(err))
    except AzureUnavailableError as err:
        # Upstream unreachable - 502 Bad Gateway.
        raise HTTPException(status_code=502, detail=f"Azure unreachable: {err}")
    except AzureTokenError as err:
        # Azure rejected the request - 502 still applies (upstream failure).
        raise HTTPException(status_code=502, detail=f"Token exchange failed: {err}")
