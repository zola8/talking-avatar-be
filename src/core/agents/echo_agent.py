import asyncio
import re
from collections.abc import AsyncGenerator

from api.models import Message
from api.models import Role
from core.agents.events import DeltaEvent
from core.agents.events import FinalEvent
from core.agents.events import SSEEvent

_TOKEN_RE = re.compile(r"\S+\s*")


class EchoAgent:
    name = "echo agent"

    async def stream(self, history: list[Message]) -> AsyncGenerator[SSEEvent, None]:
        user_turns = [m for m in history if m.role == Role.USER]
        if not user_turns:
            await asyncio.sleep(0.2)
            yield DeltaEvent("I didn't hear anything.")
            yield FinalEvent("I didn't hear anything.")
            return

        response = f"I heard you say: {user_turns[-1].content}"

        for token in _TOKEN_RE.findall(response):
            await asyncio.sleep(0.05)
            yield DeltaEvent(token)
        yield FinalEvent(response)
