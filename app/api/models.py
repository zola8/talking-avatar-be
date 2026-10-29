from enum import StrEnum

from pydantic import BaseModel
from pydantic import Field


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    # later: TOOL = "tool", FUNCTION = "function"


class Message(BaseModel):
    role: Role
    content: str


class ChatRequest(BaseModel):
    userId: str
    messages: list[Message] = Field(default_factory=list)


class ChatResponse(BaseModel):
    text: str
    role: Role = Role.ASSISTANT
