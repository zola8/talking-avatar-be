import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.responses import StreamingResponse

from api.models import ChatRequest
from core.dependencies import get_chat_service
from core.dependencies import get_current_user_id
from core.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])

KEEPALIVE_SECONDS = 15.0


def _format_sse(event: dict) -> bytes:
    """Format an event dict as an SSE message with the `event:` field."""
    event_type = event.get("type", "message")
    data = {k: v for k, v in event.items() if k != "type"}
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event_type}\ndata: {payload}\n\n".encode("utf-8")


async def _sse_stream(
    chat_service: ChatService,
    request: Request,
    user_id: str,
    req: ChatRequest,
) -> AsyncGenerator[bytes, None]:
    agen = chat_service.stream_events(user_id, req)
    try:
        while True:
            try:
                event = await asyncio.wait_for(
                    agen.__anext__(), timeout=KEEPALIVE_SECONDS
                )
            except StopAsyncIteration:
                break
            except asyncio.TimeoutError:
                if await request.is_disconnected():
                    break
                yield b": keepalive\n\n"
                continue

            if await request.is_disconnected():
                break

            yield _format_sse(event)
    except asyncio.CancelledError:
        raise
    finally:
        # Propagates CancelledError into the agent's iter() so it can
        # cancel the in-flight LLM call and clean up.
        await agen.aclose()


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    chat_service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    # Validate BEFORE opening the stream — 404 if agent unknown.
    if req.agent_id not in chat_service.agent_ids():
        raise HTTPException(
            status_code=404,
            detail=f"Unknown agent: {req.agent_id}. "
                   f"Available: {sorted(chat_service.agent_ids())}",
        )

    return StreamingResponse(
        _sse_stream(chat_service, request, user_id, req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
