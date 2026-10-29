import logging

import httpx

from app.api.models import AzureTokenResponse
from app.core.config import settings
from app.core.errors import AzureConfigError
from app.core.errors import AzureTokenError
from app.core.errors import AzureUnavailableError

logger = logging.getLogger(__name__)

_TOKEN_URL = "https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
_SUBSCRIPTION_HEADER = "Ocp-Apim-Subscription-Key"


class AzureService:
    """Issues Azure Speech tokens. Stateless — safe as a singleton."""

    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        region: str | None = None,
        key: str | None = None,
    ) -> None:
        # Pulled from settings if not injected; injection makes tests trivial.
        self._client = client
        self._region = region or settings.azure_speech_region
        self._key = key or settings.azure_speech_key

    async def issue_token(self) -> AzureTokenResponse:
        logger.info("Issuing Azure Speech token")
        self._require_config()

        url = _TOKEN_URL.format(region=self._region)
        try:
            resp = await self._client.post(
                url, headers={_SUBSCRIPTION_HEADER: self._key}
            )
        except httpx.TimeoutException as err:
            logger.warning("Azure token request timed out: %s", err)
            raise AzureUnavailableError("request timed out") from err
        except httpx.HTTPError as err:
            logger.warning("Azure token request failed: %s", err)
            raise AzureUnavailableError(str(err)) from err

        if resp.status_code != 200:
            # Log the body server-side; don't leak it to the client.
            logger.warning(
                "Azure token exchange failed: status=%s body=%s",
                resp.status_code,
                resp.text,
            )
            raise AzureTokenError(f"status={resp.status_code}")

        logger.info("Azure Speech token issued")
        return AzureTokenResponse(token=resp.text, region=self._region)

    def _require_config(self) -> None:
        if not self._key:
            logger.error("AZURE_SPEECH_KEY not configured")
            raise AzureConfigError("AZURE_SPEECH_KEY not configured")
        if not self._region:
            logger.error("AZURE_SPEECH_REGION not configured")
            raise AzureConfigError("AZURE_SPEECH_REGION not configured")
