import asyncio
import logging
from collections.abc import AsyncGenerator

from pydantic_ai import Agent
from pydantic_ai import FinalResultEvent
from pydantic_ai import FunctionToolCallEvent
from pydantic_ai import FunctionToolResultEvent
from pydantic_ai import PartDeltaEvent
from pydantic_ai import ThinkingPartDelta
from pydantic_ai.messages import ModelMessage
from pydantic_ai.messages import ModelRequest
from pydantic_ai.messages import ModelResponse
from pydantic_ai.messages import SystemPromptPart
from pydantic_ai.messages import TextPart
from pydantic_ai.messages import UserPromptPart

from api.models import Message
from api.models import Role

logger = logging.getLogger(__name__)

LLM_TIMEOUT_SECONDS = 30.0


class PydanticAIAgent:
    """Generic LLM-backed agent using PydanticAI."""

    def __init__(
        self,
        name: str,
        model: str,
        system_prompt: str | None = None,
    ) -> None:
        self.name = name
        self.model = model
        kwargs = {}
        if system_prompt:
            kwargs["system_prompt"] = system_prompt
        self._agent = Agent(model=model, **kwargs)

    async def iter(self, history: list[Message]) -> AsyncGenerator[dict, None]:
        if history and history[-1].role == Role.USER:
            user_prompt = history[-1].content
            prior_history = history[:-1]
        else:
            user_prompt = None
            prior_history = history
        pai_history = self._to_pai_messages(prior_history)

        logger.info("LLM call starting (model=%s)", self.model)
        yield {"type": "thinking", "model": self.model}

        try:
            async with asyncio.timeout(LLM_TIMEOUT_SECONDS):
                async with self._agent.iter(
                    user_prompt=user_prompt,
                    message_history=pai_history,
                ) as run:
                    async for event in self._stream_events(run):
                        yield event
            logger.info("LLM call completed")
        except asyncio.TimeoutError:
            logger.warning("LLM call timed out after %ss", LLM_TIMEOUT_SECONDS)
            raise RuntimeError(f"LLM timed out after {LLM_TIMEOUT_SECONDS}s")
        except asyncio.CancelledError:
            logger.warning("LLM call cancelled (client disconnected?)")
            raise
        except Exception as e:
            logger.warning("LLM call failed: %s", str(e)[:200])
            raise

    async def _stream_events(self, run) -> AsyncGenerator[dict, None]:
        """
        Translate PydanticAI stream events into our domain SSE events.

        Extracted from iter() so the event translation logic is separate
        from the timeout/history/loop scaffolding.
        """
        async for event in run:
            if isinstance(event, FunctionToolCallEvent):
                part = event.part
                yield {
                    "type": "tool_call",
                    "call_id": part.tool_call_id,
                    "name": part.tool_name,
                    "args": part.args,
                }
            elif isinstance(event, FunctionToolResultEvent):
                result = event.result
                yield {
                    "type": "tool_result",
                    "call_id": event.tool_call_id,
                    "name": result.tool_name,
                    "result": result.content,
                }
            elif isinstance(event, PartDeltaEvent) and isinstance(
                event.delta, ThinkingPartDelta
            ):
                yield {
                    "type": "reasoning",
                    "content": event.delta.content_delta,
                }
            elif isinstance(event, PartDeltaEvent):
                yield {
                    "type": "delta",
                    "content": event.delta.content_delta,
                }
            elif isinstance(event, FinalResultEvent):
                yield {
                    "type": "final",
                    "content": run.result.output,
                }

    @staticmethod
    def _to_pai_messages(history: list[Message]) -> list[ModelMessage]:
        result: list[ModelMessage] = []
        for m in history:
            if m.role == Role.SYSTEM:
                result.append(
                    ModelRequest(parts=[SystemPromptPart(content=m.content)])
                )
            elif m.role == Role.USER:
                result.append(
                    ModelRequest(parts=[UserPromptPart(content=m.content)])
                )
            elif m.role == Role.ASSISTANT:
                result.append(
                    ModelResponse(parts=[TextPart(content=m.content)])
                )
        return result
