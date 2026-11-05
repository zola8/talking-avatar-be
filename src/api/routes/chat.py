from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import StreamingResponse

from api.models import AgentInfo
from api.models import ChatRequest
from core.dependencies import get_chat_service
from core.dependencies import get_current_user_id
from core.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


async def _sse_stream(
    chat_service: ChatService, req: ChatRequest, user_id: str
) -> AsyncGenerator[bytes, None]:
    """
    Wrap chat_service.stream() into the Server-Sent Events wire format.

    Each token is sent as:
        data: <chunk>\n\n

    The stream is closed with:
        data: [DONE]\n\n

    Mirrors the OpenAI streaming convention so generic SSE clients work
    out of the box.
    """
    try:
        async for chunk in chat_service.stream(req, user_id):
            # SSE requires newlines; escape any literal newlines inside a
            # chunk so a single "data:" line stays a single event.
            safe = chunk.replace("\n", "\\n")
            yield f"data: {safe}\n\n".encode("utf-8")
    except Exception as e:  # noqa: BLE001 - surface to client, then close
        yield f"data: [ERROR] {e}\n\n".encode("utf-8")
    finally:
        yield b"data: [DONE]\n\n"


@router.post("/chat/stream")
async def chat(
    req: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    chat_service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    return StreamingResponse(
        _sse_stream(chat_service, req, user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.get("/agents", response_model=list[AgentInfo])
async def list_agents(
    chat_service: ChatService = Depends(get_chat_service),
) -> list[AgentInfo]:
    """List all registered agents.    """
    return chat_service.list_agents()


@router.get("/conversations")
async def list_conversations(
    chat_service: ChatService = Depends(get_chat_service),
) -> list[dict]:
    """List every (user, agent) conversation with message counts."""
    return await chat_service.list_conversations()


@router.get("/conversations/{user_id}/{agent_id}")
async def get_conversation(
    user_id: str,
    agent_id: str,
    chat_service: ChatService = Depends(get_chat_service),
) -> dict:
    """Dump the full message history for one conversation."""
    messages = await chat_service.get_conversation(user_id, agent_id)
    return {
        "userId": user_id,
        "agentId": agent_id,
        "messageCount": len(messages),
        "messages": [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ],
    }


@router.delete("/conversations/{user_id}/{agent_id}")
async def clear_conversation(
    user_id: str,
    agent_id: str,
    chat_service: ChatService = Depends(get_chat_service),
) -> dict:
    """Wipe one conversation's history."""
    await chat_service.clear_conversation(user_id, agent_id)
    return {"status": "cleared", "userId": user_id, "agentId": agent_id}
