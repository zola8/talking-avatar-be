import httpx

from app.core.agents.echo_agent import EchoAgent
from app.core.azure.service import AzureService
from app.core.services.chat_service import ChatService

_agent = EchoAgent()
_service = ChatService(agent=_agent)
_azure_http = httpx.AsyncClient(timeout=10.0)
_azure_service = AzureService(client=_azure_http)


def get_chat_service() -> ChatService:
    return _service


def get_azure_service() -> AzureService:
    return _azure_service


async def close_http_clients() -> None:
    await _azure_http.aclose()
