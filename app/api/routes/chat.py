import asyncio

from fastapi import APIRouter

from app.api.models import ChatRequest
from app.api.models import ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    await asyncio.sleep(0.6)

    # Find the latest user message
    user_messages = [m for m in req.messages if m.role == "user"]
    if not user_messages:
        return ChatResponse(text="I didn't hear anything.")

    last_user_message = user_messages[-1].content
    return ChatResponse(text=f"I heard you say: {last_user_message}")
