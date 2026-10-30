import asyncio

from api.models import Message
from api.models import Role


class EchoAgent:
    name = "echo"

    async def respond(self, history: list[Message]) -> Message:
        await asyncio.sleep(0.6)

        user_turns = [m for m in history if m.role == Role.USER]
        if not user_turns:
            return Message(role=Role.ASSISTANT, content="I didn't hear anything.")
        return Message(
            role=Role.ASSISTANT,
            content=f"I heard you say: {user_turns[-1].content}",
        )
