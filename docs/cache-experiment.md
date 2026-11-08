# P08 experiment: cache and scale

This file is the place for the measurements. The numbers come from running `measure.py` on your laptop;
they are not estimated. Fill in the table after each run. Until then the table stays empty.

## Method
1. `docker compose up -d` (PostgreSQL and Redis 8).
2. Without the cache: the cache code is bypassed by `HOTEL_REDIS_URL` pointing at a port with nothing listening,
   or by temporarily returning `load()` directly in `AvailabilityCache.free_room_numbers`. Restart `python main.py`.
   Run `python measure.py --runs 1000`. Record the result in row A.
3. With the cache: `docker compose exec cache redis-cli FLUSHALL`, restart `python main.py` (counters start at zero),
   then `python measure.py --runs 1000`. Record the result in row B.

## Results
| Run | Searches | Average | p95 | dbQueries | cacheHits | cacheMisses |
|---|---|---|---|---|---|---|
| A: no cache | 1,000 | | | | | |
| B: Redis cache, empty at start | 1,000 | | | | | |

Expected from the design, to compare with your run: run A makes 2,000 database queries (2 rooms per search);
run B makes 2 queries (one miss per room set) and 999 hits. If your numbers differ, explain why here.

## Stale result (the bug the version number prevents)
1. Book R7 for 12–14 Nov: `POST /reservations` with Maya (201).
2. Search 12–14 Nov again. With the invalidation in `api.py` (`availability.invalidate()` after a booking), only R8 is listed.
3. To see the bug, comment out the `availability.invalidate()` call in `reserve`, restart, and repeat steps 1–2 with
   a search before the booking. R7 is still listed. Then `POST` Omar for R7 (409): the booking reads PostgreSQL,
   so the double booking is refused even though the search was stale.
4. Write what you observed here: the search result before and after, and the status code of Omar's booking.

## Hot key and next bottleneck
Write here, from your own measurements or the code: which key is hottest, what the version change costs under
many bookings, and what would break first if the hotel had 10 times more searches (P09 covers the next step).
