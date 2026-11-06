import asyncio
import logging
from collections.abc import AsyncGenerator

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
from pydantic_ai.messages import ModelRequest
from pydantic_ai.messages import ModelResponse
from pydantic_ai.messages import SystemPromptPart
from pydantic_ai.messages import TextPart
from pydantic_ai.messages import UserPromptPart

from api.models import Message
from api.models import Role
from core.agents.events import SSEEvent
from core.agents.events import ThinkingEvent
from core.agents.pydantic_ai_translator import PydanticAIEventTranslator

logger = logging.getLogger(__name__)

LLM_TIMEOUT_SECONDS = 30.0


class PydanticAIAgent:
    """Generic LLM-backed agent using PydanticAI."""

    def __init__(
        self,
        name: str,
        model: str,
        system_prompt: str | None = None,
        translator: PydanticAIEventTranslator | None = None,
    ) -> None:
        self.name = name
        self.model = model
        kwargs = {}
        if system_prompt:
            kwargs["system_prompt"] = system_prompt
        self._agent = Agent(model=model, **kwargs)
        self._translator = translator or PydanticAIEventTranslator()

    async def stream(self, history: list[Message]) -> AsyncGenerator[SSEEvent, None]:
        if history and history[-1].role == Role.USER:
            user_prompt = history[-1].content
            prior_history = history[:-1]
        else:
            user_prompt = None
            prior_history = history
        pai_history = self._to_pai_messages(prior_history)

        logger.info("LLM call starting (model=%s)", self.model)
        yield ThinkingEvent(model=self.model)

        try:
            async with asyncio.timeout(LLM_TIMEOUT_SECONDS):
                async with self._agent.run_stream_events(
                    user_prompt=user_prompt,
                    message_history=pai_history,
                ) as events:
                    async for event in self._translator.translate(events):
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
