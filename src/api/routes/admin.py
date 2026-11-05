from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel

from api.models import AgentInfo
from core.dependencies import get_chat_service
from core.services.chat_service import ChatService

router = APIRouter(tags=["admin"])


class ConversationSummary(BaseModel):
    userId: str
    agentId: str
    conversationId: str
    messageCount: int


class ConversationDetail(BaseModel):
    userId: str
    agentId: str
    conversationId: str
    messageCount: int
    messages: list[dict]


@router.get("/agents", response_model=list[AgentInfo])
async def list_agents(
    chat_service: ChatService = Depends(get_chat_service),
) -> list[AgentInfo]:
    return chat_service.list_agents()


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    chat_service: ChatService = Depends(get_chat_service),
) -> list[ConversationSummary]:
    return [
        ConversationSummary(**row)
        for row in await chat_service.list_conversations()
    ]


@router.get(
    "/conversations/{user_id}/{agent_id}/{conversation_id}",
    response_model=ConversationDetail,
)
async def get_conversation(
    user_id: str,
    agent_id: str,
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationDetail:
    messages = await chat_service.get_conversation(user_id, agent_id, conversation_id)
    return ConversationDetail(
        userId=user_id,
        agentId=agent_id,
        conversationId=conversation_id,
        messageCount=len(messages),
        messages=[
            {"role": m.role.value, "content": m.content, "status": m.status}
            for m in messages
        ],
    )


@router.delete("/conversations/{user_id}/{agent_id}/{conversation_id}")
async def clear_conversation(
    user_id: str,
    agent_id: str,
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service),
) -> dict:
    await chat_service.clear_conversation(user_id, agent_id, conversation_id)
    return {
        "status": "cleared",
        "userId": user_id,
        "agentId": agent_id,
        "conversationId": conversation_id,
    }
