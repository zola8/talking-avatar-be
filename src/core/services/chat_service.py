from api.models import ChatRequest
from api.models import Message
from core.agents.base import Agent


class ChatService:
    def __init__(self, agent: Agent) -> None:
        self._agent = agent

    async def handle(self, req: ChatRequest) -> Message:
        return await self._agent.respond(req.messages)
