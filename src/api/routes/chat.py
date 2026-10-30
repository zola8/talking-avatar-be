from fastapi import APIRouter
from fastapi import Depends

from src.core.dependencies import get_chat_service
from src.api.models import ChatRequest
from src.api.models import ChatResponse
from src.core.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, chat_service: ChatService = Depends(get_chat_service)) -> ChatResponse:
    msg = await chat_service.handle(req)
    return ChatResponse(text=msg.content, role=msg.role)
