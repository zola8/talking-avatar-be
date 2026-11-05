from collections.abc import AsyncGenerator

from api.models import AgentInfo
from api.models import ChatRequest
from api.models import Message
from api.models import Role
from core.agents.base import Agent
from core.services.history_store import HistoryStore


class ChatService:
    def __init__(
        self,
        agents: dict[str, Agent],
        history_store: HistoryStore,
    ) -> None:
        self._agents = agents
        self._history = history_store

    def list_agents(self) -> list[AgentInfo]:
        return [
            AgentInfo(agentId=aid, name=a.name)
            for aid, a in self._agents.items()
        ]

    async def stream(
        self, req: ChatRequest, user_id: str
    ) -> AsyncGenerator[str, None]:
        agent = self._agents.get(req.agentId)
        if agent is None:
            yield f"Unknown agent: {req.agentId}"
            return

        history = await self._history.load(user_id, req.agentId)
        history.append(Message(role=Role.USER, content=req.content))

        chunks: list[str] = []
        async for chunk in agent.stream(history):
            chunks.append(chunk)
            yield chunk

        history.append(Message(role=Role.ASSISTANT, content="".join(chunks)))
        await self._history.save(user_id, req.agentId, history)

    async def list_conversations(self) -> list[dict]:
        all_data = await self._history.all()
        return [
            {"userId": uid, "agentId": aid, "messageCount": len(msgs)}
            for (uid, aid), msgs in all_data.items()
        ]

    async def get_conversation(self, user_id: str, agent_id: str) -> list[Message]:
        return await self._history.load(user_id, agent_id)

    async def clear_conversation(self, user_id: str, agent_id: str) -> None:
        await self._history.clear(user_id, agent_id)
