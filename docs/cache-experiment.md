# P08 experiment: cache and scale

The numbers below were measured with `measure.py` (1,000 searches for 12–14 Nov, then `GET /stats`).
Both runs used the same code, the same database rows and the same machine, one after the other.

## Environment of this run (not the Docker setup from docker-compose.yml)
Docker is not installed on the laptop, so the run used the same software without containers:
- PostgreSQL 18.6, from the `@embedded-postgres/linux-arm64` npm package (same major version as `postgres:18` in docker-compose.yml). `db/init.sql` was loaded unchanged.
- Redis 6.2.14, from the `redislite` Python package. docker-compose.yml asks for Redis 8, which was not available here.
- Linux aarch64 VM on the laptop, 4 CPUs, app and databases on localhost, one client at a time.
So the absolute times are not the same as a Docker run on macOS. Compare run A with run B, not with other machines.

## Method
1. Run A, no cache: `HOTEL_CACHE=off python main.py`, then `python measure.py --runs 1000`.
   With the switch set, every search goes straight to PostgreSQL (`NoCache` in `hotel_booking/availability.py`).
2. Run B, cache on, cold start: Redis emptied with `FLUSHALL`, then `python main.py`, then `python measure.py --runs 1000`.
   The counters start at zero because the app was restarted.
With Docker, the same steps are `docker compose up -d`, `docker compose exec cache redis-cli FLUSHALL`, and the same commands.

## Results
| Run | Searches | Average | p95 | dbQueries | cacheHits | cacheMisses |
|---|---|---|---|---|---|---|
| A: no cache | 1,000 | 2.20 ms | 2.68 ms | 2,000 | 0 | 1,000 |
| B: Redis cache, empty at start | 1,000 | 1.19 ms | 1.47 ms | 2 | 999 | 1 |

What the numbers show:
- The database query count matches the design: 2 queries for 1,000 searches with the cache (one miss, one query per room), against 2,000 without it.
- Average and p95 are about 45% lower with the cache. Both are far below the S1 target of p95 ≤ 1 second (quality-scenarios.md). At this size, with the database on the same machine, the cache saves time but does not decide whether S1 is met. The benefit grows when the database is remote or busy.
- S6 asks for at least 20% less energy per 1,000 searches. Energy was not measured here, so S6 is not checked yet (P24).

## Stale result (the bug the version number prevents)
Run on the same PostgreSQL and Redis, with the same code (script in the scratch folder, output copied here):

```text
== With the fix (invalidate after booking)
search before booking: ['R7', 'R8']
Maya books R7: 201 {'id': 'R101', 'status': 'Confirmed', 'notificationFailed': False}
search after booking:  ['R8']
Omar books R7 13-15: 409 Unavailable

== Without the fix (invalidate disabled)
search before booking: ['R7', 'R8']
Maya books R7: 201 {'id': 'R101', 'status': 'Confirmed', 'notificationFailed': False}
search after booking (stale?): ['R7', 'R8']
Omar books R7 13-15: 409 Unavailable
```

What this shows:
- Without the fix, the search still lists R7 after Maya's booking. The stale result is real.
- Omar's booking is still refused with 409, because the booking reads PostgreSQL and not the cache. A stale search cannot cause a double booking, but it can mislead a guest.
- The stale answer is only removed by the TTL (30 seconds) or by the next version change. Without the fix, nothing else clears it.

## Hot key and next bottleneck
- Hot key: every booking and cancellation changes the one global version. After a booking, every date range is cold at the same time, so the next searches for popular nights all miss at once (a cache stampede). The fix is cheap but not free.
- Known race in the design: a search that started before a booking can write its old answer under the new version. That answer stays at most 30 seconds. The booking itself is safe.
- Next bottleneck: the database check in the booking itself (`has_overlap`), which runs on every booking and is not cached. P09 moves that rule into PostgreSQL, where it can be made safe under concurrent requests.
- With 10 times more searches, the cache hides most reads. The first thing to break would be the single Redis server and the global version, not the database for searches.
