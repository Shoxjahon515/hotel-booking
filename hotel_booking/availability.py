"""Cache-aside for the free-room search (P08).

The answer to "which rooms are free for these nights" is kept in Redis for 30 seconds. The key
holds a version number. A booking or a cancellation raises the version, so every cached answer
under the old version is no longer read. Only the room numbers are cached: the booking rule
still runs against PostgreSQL, so a stale search can never double-book a room.
"""
from __future__ import annotations

import json
from typing import Callable, Protocol

from hotel_booking.reservations import DateRange
from hotel_booking.stats import Stats

TTL_SECONDS = 30
VERSION_KEY = "availability:version"


class KeyValueCache(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str, ttl_seconds: int) -> None: ...
    def incr(self, key: str) -> int: ...


class InMemoryCache:
    """A dictionary, for the tests. It ignores the TTL."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._data[key] = value

    def incr(self, key: str) -> int:
        self._data[key] = str(int(self._data.get(key, "0")) + 1)
        return int(self._data[key])


class RedisCache:
    """Redis through redis-py. The client must be created with decode_responses=True."""

    def __init__(self, client) -> None:
        self._client = client

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._client.set(key, value, ex=ttl_seconds)

    def incr(self, key: str) -> int:
        return int(self._client.incr(key))


class AvailabilityCache:
    def __init__(self, cache: KeyValueCache, stats: Stats, ttl_seconds: int = TTL_SECONDS) -> None:
        self._cache = cache
        self._stats = stats
        self._ttl = ttl_seconds

    def free_room_numbers(self, stay: DateRange, load: Callable[[], list[str]]) -> list[str]:
        """Cache-aside: read Redis; on a miss, call load() (PostgreSQL) and keep its answer for the TTL."""
        version = self._cache.get(VERSION_KEY) or "0"
        key = f"availability:v{version}:{stay.check_in.isoformat()}:{stay.check_out.isoformat()}"
        cached = self._cache.get(key)
        if cached is not None:
            self._stats.cache_hits += 1
            return json.loads(cached)
        self._stats.cache_misses += 1
        numbers = load()
        self._cache.set(key, json.dumps(numbers), self._ttl)
        return numbers

    def invalidate(self) -> None:
        """Call after every successful booking or cancellation: old cached answers stop being read."""
        self._cache.incr(VERSION_KEY)
