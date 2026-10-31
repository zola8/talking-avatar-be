from collections.abc import AsyncGenerator

import httpx

from core.agents.echo_agent import EchoAgent
from core.services.azure_service import AzureService
from core.services.chat_service import ChatService

_agent = EchoAgent()
_service = ChatService(agent=_agent)


def get_chat_service() -> ChatService:
    return _service


async def get_azure_service() -> AsyncGenerator[AzureService, None]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        yield AzureService(client=client)
