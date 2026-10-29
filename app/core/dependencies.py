from app.core.agents.echo_agent import EchoAgent
from app.core.services.chat_service import ChatService

_agent = EchoAgent()
_service = ChatService(agent=_agent)


def get_chat_service() -> ChatService:
    return _service
