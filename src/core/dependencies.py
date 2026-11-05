import logging
from collections.abc import AsyncGenerator

import httpx
from fastapi import HTTPException
from fastapi import Header

from core.agents.base import Agent
from core.agents.echo_agent import EchoAgent
from core.services.azure_service import AzureService
from core.services.chat_service import ChatService
from core.services.history_store import HistoryStore
from core.services.history_store import InMemoryHistoryStore

logger = logging.getLogger(__name__)

# --- Agent registry (singletons) ---
_agents: dict[str, Agent] = {
    "echo": EchoAgent(),
}

_history_store: HistoryStore = InMemoryHistoryStore(max_messages=100)

_chat_service = ChatService(agents=_agents, history_store=_history_store)


def get_history_store() -> HistoryStore:
    return _history_store


def get_chat_service() -> ChatService:
    return _chat_service


async def get_azure_service() -> AsyncGenerator[AzureService, None]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        yield AzureService(client=client)


async def get_current_user_id(x_user_id: str | None = Header(default=None)) -> str:
    """
    Demo: trust the X-User-Id header.
    Prod: replace with JWT decoding from Authorization header.
    """
    if not x_user_id:
        logger.error("Missing user identity")
        raise HTTPException(status_code=401, detail="Missing user identity")
    return x_user_id
    # return "test-user-id"
