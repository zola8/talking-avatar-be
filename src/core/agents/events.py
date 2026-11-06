from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SSEEvent:
    """Base type for all SSE events.

    Concrete subclasses implement :meth:`to_dict`. Use ``isinstance`` checks
    or ``type(event)`` for dispatch; do not rely on a ``type`` attribute on
    the base class.
    """

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass(frozen=True)
class ThinkingEvent(SSEEvent):
    """Sent once at the start of an LLM run, carries the model identifier."""

    model: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": "thinking", "model": self.model}


@dataclass(frozen=True)
class ReasoningEvent(SSEEvent):
    """A chunk of model chain-of-thought / thinking content."""

    content: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": "reasoning", "content": self.content}


@dataclass(frozen=True)
class DeltaEvent(SSEEvent):
    """An incremental content chunk for the assistant message."""

    content: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": "delta", "content": self.content}


@dataclass(frozen=True)
class FinalEvent(SSEEvent):
    """Marks the end of a run; carries the full final message."""

    content: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": "final", "content": self.content}


@dataclass(frozen=True)
class ToolCallEvent(SSEEvent):
    """The model requested a tool invocation."""

    call_id: str
    name: str
    args: Any

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "tool_call",
            "call_id": self.call_id,
            "name": self.name,
            "args": self.args,
        }


@dataclass(frozen=True)
class ToolResultEvent(SSEEvent):
    """A tool returned a result for a previous ``tool_call``."""

    call_id: str
    name: str
    result: Any

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "tool_result",
            "call_id": self.call_id,
            "name": self.name,
            "result": self.result,
        }
