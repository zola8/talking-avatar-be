from enum import StrEnum

from pydantic import BaseModel


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


class ChatRequest(BaseModel):
    agentId: str
    content: str


class ChatResponse(BaseModel):
    text: str
    role: Role = Role.ASSISTANT


class AgentInfo(BaseModel):
    agentId: str
    name: str
