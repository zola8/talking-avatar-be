from enum import StrEnum

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class AzureTokenResponse(BaseModel):
    token: str
    region: str


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    role: Role
    content: str
    status: str = "complete"  # "pending" | "complete"
    client_message_id: str | None = None


class ChatRequest(BaseModel):
    agent_id: str = Field(alias="agentId")
    conversation_id: str | None = Field(default=None, alias="conversationId")
    client_message_id: str | None = Field(default=None, alias="clientMessageId")
    content: str = Field(min_length=1, max_length=10_000)
    model_config = ConfigDict(populate_by_name=True)


class ChatResponse(BaseModel):
    text: str
    role: Role = Role.ASSISTANT


class AgentInfo(BaseModel):
    agentId: str
    name: str
