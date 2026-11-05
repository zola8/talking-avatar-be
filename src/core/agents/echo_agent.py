import asyncio
import re
from collections.abc import AsyncGenerator

from api.models import Message
from api.models import Role


class EchoAgent:
    name = "echo agent"

    async def stream(self, history: list[Message]) -> AsyncGenerator[str, None]:
        user_turns = [m for m in history if m.role == Role.USER]
        if not user_turns:
            yield "I didn't hear anything."
            return

        response = f"I heard you say: {user_turns[-1].content}"

        for token in re.findall(r"\S+\s*", response):
            await asyncio.sleep(0.05)
            yield token
