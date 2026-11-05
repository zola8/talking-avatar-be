import asyncio
from typing import Protocol

from api.models import Message


class HistoryStore(Protocol):
    async def load(self, user_id: str, agent_id: str) -> list[Message]: ...

    async def save(
        self, user_id: str, agent_id: str, history: list[Message]
    ) -> None: ...

    # Debug-only
    async def keys(self) -> list[tuple[str, str]]: ...

    async def all(self) -> dict[tuple[str, str], list[Message]]: ...

    async def clear(self, user_id: str, agent_id: str) -> None: ...

    async def clear_all(self) -> None: ...


class InMemoryHistoryStore:
    """
    Simple in-memory history store.

    - Singleton: create one and share it across requests.
    - Keyed by (user_id, agent_id) — one conversation per user+agent pair.
    - Async-safe via a single asyncio.Lock (fine for single-process demo).
    - Caps history to the last N messages to avoid unbounded growth.
    - load()/save() return/take defensive copies so callers can't mutate
      the stored list by accident.
    """

    def __init__(self, max_messages: int = 100) -> None:
        self._max = max_messages
        self._store: dict[tuple[str, str], list[Message]] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _key(user_id: str, agent_id: str) -> tuple[str, str]:
        return (user_id, agent_id)

    async def load(self, user_id: str, agent_id: str) -> list[Message]:
        async with self._lock:
            return list(self._store.get(self._key(user_id, agent_id), []))

    async def save(
        self, user_id: str, agent_id: str, history: list[Message]
    ) -> None:
        async with self._lock:
            trimmed = history[-self._max:] if self._max > 0 else list(history)
            self._store[self._key(user_id, agent_id)] = list(trimmed)

    async def keys(self) -> list[tuple[str, str]]:
        async with self._lock:
            return list(self._store.keys())

    async def all(self) -> dict[tuple[str, str], list[Message]]:
        async with self._lock:
            return {k: list(v) for k, v in self._store.items()}

    async def clear(self, user_id: str, agent_id: str) -> None:
        async with self._lock:
            self._store.pop(self._key(user_id, agent_id), None)

    async def clear_all(self) -> None:
        async with self._lock:
            self._store.clear()
