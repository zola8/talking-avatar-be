import logging
import os

import httpx

from api.models import AzureTokenResponse
from core.errors import AzureConfigError
from core.errors import AzureTokenError
from core.errors import AzureUnavailableError

logger = logging.getLogger(__name__)

_TOKEN_URL = "https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
_SUBSCRIPTION_HEADER = "Ocp-Apim-Subscription-Key"
_DEFAULT_REGION = "westeurope"


class AzureService:
    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        region: str | None = None,
        key: str | None = None,
    ) -> None:
        self._client = client
        self._region_override = region
        self._key_override = key

    async def issue_token(self) -> AzureTokenResponse:
        region = self._region_override or os.getenv("AZURE_SPEECH_REGION", _DEFAULT_REGION)
        key = self._key_override or os.getenv("AZURE_SPEECH_KEY", "")

        logger.info("Issuing Azure Speech token for region=%s", region)
        if not key:
            logger.error("AZURE_SPEECH_KEY not configured")
            raise AzureConfigError("AZURE_SPEECH_KEY not configured")
        if not region:
            raise AzureConfigError("AZURE_SPEECH_REGION not configured")

        url = _TOKEN_URL.format(region=region)
        try:
            resp = await self._client.post(url, headers={_SUBSCRIPTION_HEADER: key})
        except httpx.TimeoutException as err:
            logger.warning("Azure token request timed out: %s", err)
            raise AzureUnavailableError("request timed out") from err
        except httpx.HTTPError as err:
            logger.warning("Azure token request failed: %s", err)
            raise AzureUnavailableError(str(err)) from err

        if resp.status_code != 200:
            logger.warning(
                "Azure token exchange failed: status=%s body=%s",
                resp.status_code, resp.text,
            )
            raise AzureTokenError(f"status={resp.status_code}")

        logger.info("Azure Speech token issued")
        return AzureTokenResponse(token=resp.text, region=region)
