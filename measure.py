"""P08 measurement: 1,000 free-room searches for 12-14 Nov, then GET /stats.

Start the stack first:  docker compose up -d  and  python main.py
For a cold run, empty Redis and restart main.py (the counters start at zero):
    docker compose exec cache redis-cli FLUSHALL
Then run:  python measure.py --runs 1000
"""
from __future__ import annotations

import math
import statistics
import sys
import time

import httpx

BASE = "http://localhost:5080"
SEARCH = {"checkIn": "2026-11-12", "checkOut": "2026-11-14"}


def main() -> None:
    runs = int(sys.argv[sys.argv.index("--runs") + 1]) if "--runs" in sys.argv else 1000
    timings: list[float] = []
    with httpx.Client(base_url=BASE, timeout=10) as client:
        for _ in range(runs):
            started = time.perf_counter()
            response = client.get("/rooms/availability", params=SEARCH)
            timings.append((time.perf_counter() - started) * 1000)
            response.raise_for_status()
        counters = client.get("/stats").json()
    ordered = sorted(timings)
    p95 = ordered[math.ceil(0.95 * len(ordered)) - 1]  # nearest rank
    print(f"searches: {runs}")
    print(f"average: {statistics.fmean(timings):.2f} ms")
    print(f"p95: {p95:.2f} ms")
    print(f"GET /stats: {counters}")


if __name__ == "__main__":
    main()
