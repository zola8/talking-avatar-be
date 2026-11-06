from typing import AsyncGenerator
from typing import Protocol

from api.models import Message


class Agent(Protocol):
    name: str

    def stream(self, history: list[Message]) -> AsyncGenerator[dict, None]:
        ...
