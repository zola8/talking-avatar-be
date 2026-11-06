import asyncio
import logging
import uuid
from collections.abc import AsyncGenerator

from api.models import AgentInfo
from api.models import ChatRequest
from api.models import Message
from api.models import Role
from core.agents.base import Agent
from core.agents.events import DeltaEvent
from core.agents.events import FinalEvent
from core.services.history_store import HistoryStore

logger = logging.getLogger(__name__)


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

    def agent_ids(self) -> set[str]:
        return set(self._agents.keys())

    async def list_conversations(self) -> list[dict]:
        all_data = await self._history.all()
        return [
            {
                "userId": uid,
                "agentId": aid,
                "conversationId": cid,
                "messageCount": len(msgs),
            }
            for (uid, aid, cid), msgs in all_data.items()
        ]

    async def get_conversation(
        self, user_id: str, agent_id: str, conversation_id: str
    ) -> list[Message]:
        return await self._history.load(user_id, agent_id, conversation_id)

    async def clear_conversation(
        self, user_id: str, agent_id: str, conversation_id: str
    ) -> None:
        await self._history.clear(user_id, agent_id, conversation_id)

    async def stream_events(
        self, user_id: str, req: ChatRequest
    ) -> AsyncGenerator[dict, None]:
        conversation_id = req.conversation_id or str(uuid.uuid4())
        yield {"type": "meta", "conversation_id": conversation_id}

        user_msg = Message(
            role=Role.USER,
            content=req.content,
            status="pending",
            client_message_id=req.client_message_id,
        )
        history = await self._history.append_and_load(
            user_id, req.agent_id, conversation_id, user_msg
        )

        chunks: list[str] = []
        final_content: str | None = None

        try:
            async for event in self._agents[req.agent_id].stream(history):
                if isinstance(event, DeltaEvent):
                    chunks.append(event.content)
                elif isinstance(event, FinalEvent):
                    final_content = event.content
                yield event.to_dict()
        except asyncio.CancelledError:
            # Client disconnected; user message stays pending, filtered next load.
            raise
        except Exception as e:
            logger.exception("Agent stream failed")
            yield {"type": "error", "message": str(e)}
            return  # do not persist, do not yield done

        assistant_text = (
            final_content if final_content is not None else "".join(chunks)
        )
        assistant_msg = Message(role=Role.ASSISTANT, content=assistant_text)
        await self._history.append_assistant(
            user_id, req.agent_id, conversation_id, assistant_msg
        )

        yield {"type": "done"}
