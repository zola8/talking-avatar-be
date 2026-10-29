import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.api.models import AzureTokenResponse
from app.core.dependencies import get_azure_service
from app.core.errors import AzureConfigError
from app.core.errors import AzureTokenError
from app.core.errors import AzureUnavailableError
from app.core.services.azure_service import AzureService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/azure", tags=["azure"])


@router.post("/token")
async def get_azure_token(
    svc: AzureService = Depends(get_azure_service),
) -> AzureTokenResponse:
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
