import asyncio
import re
from collections.abc import AsyncGenerator

from api.models import Message
from api.models import Role


class EchoAgent:
    name = "echo agent"

    async def iter(self, history: list[Message]) -> AsyncGenerator[dict, None]:
        user_turns = [m for m in history if m.role == Role.USER]
        if not user_turns:
            await asyncio.sleep(0.2)
            yield {"type": "delta", "content": "I didn't hear anything."}
            yield {"type": "final", "content": "I didn't hear anything."}
            return

        response = f"I heard you say: {user_turns[-1].content}"
        for token in re.findall(r"\S+\s*", response):
            await asyncio.sleep(0.05)
            yield {"type": "delta", "content": token}
        yield {"type": "final", "content": response}
