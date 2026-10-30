from typing import Protocol

from api.models import Message


class Agent(Protocol):
    name: str

    async def respond(self, history: list[Message]) -> Message: ...
