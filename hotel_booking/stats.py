"""Counters for GET /stats (P08). They start at zero each time the app starts."""
from __future__ import annotations


class Stats:
    def __init__(self) -> None:
        self.db_queries = 0    # one per has_overlap call that reaches PostgreSQL
        self.cache_hits = 0    # searches answered from Redis
        self.cache_misses = 0  # searches that had to ask PostgreSQL

    def snapshot(self) -> dict[str, int]:
        return {"dbQueries": self.db_queries, "cacheHits": self.cache_hits, "cacheMisses": self.cache_misses}
