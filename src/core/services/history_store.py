import asyncio
from typing import Protocol

from api.models import Message
from api.models import Role

Key = tuple[str, str, str]


class HistoryStore(Protocol):
    async def load(
        self, user_id: str, agent_id: str, conversation_id: str
    ) -> list[Message]: ...

    async def append_and_load(
        self,
        user_id: str,
        agent_id: str,
        conversation_id: str,
        msg: Message,
    ) -> list[Message]: ...

    async def append_assistant(
        self,
        user_id: str,
        agent_id: str,
        conversation_id: str,
        msg: Message,
    ) -> None: ...

    async def keys(self) -> list[Key]: ...

    async def all(self) -> dict[Key, list[Message]]: ...

    async def clear(
        self, user_id: str, agent_id: str, conversation_id: str
    ) -> None: ...

    async def clear_all(self) -> None: ...


class InMemoryHistoryStore:
    """
    In-memory history store.

    - Singleton: create one and share it across requests.
    - Keyed by (user_id, agent_id, conversation_id).
    - Async-safe via a single asyncio.Lock (fine for single-process demo).
    - Caps history to the last N messages.
    - Never mutates stored Message objects: status flips replace the
      message with a new instance via model_copy(update=...).
    - load()/append_and_load() return defensive copies of the list;
      callers can mutate the returned list without affecting storage.
    """

    def __init__(self, max_messages: int = 100) -> None:
        self._max = max_messages
        self._store: dict[Key, list[Message]] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _key(user_id: str, agent_id: str, conversation_id: str) -> Key:
        return (user_id, agent_id, conversation_id)

    def _trim(self, msgs: list[Message]) -> list[Message]:
        if self._max > 0 and len(msgs) > self._max:
            return msgs[-self._max:]
        return msgs

    async def load(
        self, user_id: str, agent_id: str, conversation_id: str
    ) -> list[Message]:
        async with self._lock:
            msgs = self._store.get(self._key(user_id, agent_id, conversation_id), [])
            # Drop orphan pending user turns (crashed streams).
            return [
                m for m in msgs
                if not (m.role == Role.USER and m.status == "pending")
            ]

    async def append_and_load(
        self,
        user_id: str,
        agent_id: str,
        conversation_id: str,
        msg: Message,
    ) -> list[Message]:
        key = self._key(user_id, agent_id, conversation_id)
        async with self._lock:
            existing = list(self._store.get(key, []))

            # Idempotency: if client_message_id already stored, don't re-add.
            if msg.client_message_id and any(
                m.client_message_id == msg.client_message_id for m in existing
            ):
                return list(existing)

            existing.append(msg)
            self._store[key] = self._trim(existing)
            return list(self._store[key])

    async def append_assistant(
        self,
        user_id: str,
        agent_id: str,
        conversation_id: str,
        msg: Message,
    ) -> None:
        key = self._key(user_id, agent_id, conversation_id)
        async with self._lock:
            existing = list(self._store.get(key, []))

            # Replace the last pending user message with a "complete" copy.
            # We do NOT mutate the original Message instance.
            for i in range(len(existing) - 1, -1, -1):
                m = existing[i]
                if m.role == Role.USER and m.status == "pending":
                    existing[i] = m.model_copy(update={"status": "complete"})
                    break

            existing.append(msg)
            self._store[key] = self._trim(existing)

    async def keys(self) -> list[Key]:
        async with self._lock:
            return list(self._store.keys())

    async def all(self) -> dict[Key, list[Message]]:
        async with self._lock:
            return {k: list(v) for k, v in self._store.items()}

    async def clear(
        self, user_id: str, agent_id: str, conversation_id: str
    ) -> None:
        async with self._lock:
            self._store.pop(self._key(user_id, agent_id, conversation_id), None)

    async def clear_all(self) -> None:
        async with self._lock:
            self._store.clear()
