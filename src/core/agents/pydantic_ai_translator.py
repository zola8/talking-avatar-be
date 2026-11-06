from collections.abc import AsyncGenerator
from typing import Any

from pydantic_ai import AgentRunResultEvent
from pydantic_ai import FunctionToolCallEvent
from pydantic_ai import FunctionToolResultEvent
from pydantic_ai import PartDeltaEvent
from pydantic_ai import PartStartEvent
from pydantic_ai import TextPart
from pydantic_ai import TextPartDelta
from pydantic_ai import ThinkingPart
from pydantic_ai import ThinkingPartDelta

from core.agents.events import DeltaEvent
from core.agents.events import FinalEvent
from core.agents.events import ReasoningEvent
from core.agents.events import SSEEvent
from core.agents.events import ToolCallEvent
from core.agents.events import ToolResultEvent


class PydanticAIEventTranslator:
    """Convert a PydanticAI run's events into typed SSE events."""

    async def translate(self, events: Any) -> AsyncGenerator[SSEEvent, None]:
        async for event in events:
            mapped = self._map_event(event)
            if mapped is not None:
                yield mapped

    def _map_event(self, event: Any) -> SSEEvent | None:
        if isinstance(event, PartStartEvent):
            part = event.part
            if isinstance(part, TextPart) and part.content:
                return DeltaEvent(content=part.content)
            if isinstance(part, ThinkingPart) and part.content:
                return ReasoningEvent(content=part.content)
            return None

        if isinstance(event, PartDeltaEvent):
            delta = event.delta
            if isinstance(delta, ThinkingPartDelta):
                if delta.content_delta:
                    return ReasoningEvent(content=delta.content_delta)
                return None
            if isinstance(delta, TextPartDelta):
                return DeltaEvent(content=delta.content_delta)
            return None

        # --- Tool calls / results ----------------------------------------
        if isinstance(event, FunctionToolCallEvent):
            part = event.part
            return ToolCallEvent(
                call_id=part.tool_call_id,
                name=part.tool_name,
                args=part.args,
            )

        if isinstance(event, FunctionToolResultEvent):
            part = event.part
            return ToolResultEvent(
                call_id=part.tool_call_id,
                name=part.tool_name,
                result=part.content,
            )

        # --- Final output ------------------------------------------------
        if isinstance(event, AgentRunResultEvent):
            output = event.result.output
            return FinalEvent(content=output if isinstance(output, str) else str(output))

        return None
