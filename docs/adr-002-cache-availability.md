# ADR-002: Cache the free-room search in Redis, with a version number

Status: Accepted, 8 November 2026

## Context
The search for free rooms asks PostgreSQL once per room (S1: p95 at most 1 second at peak, see
docs/capacity.md). Most searches repeat the same few date ranges. A booking must still be
checked against PostgreSQL (S2: no double booking), so the cache may only answer searches,
never the booking rule itself.

## Decision
- Cache-aside: Redis is asked first. On a miss the app asks PostgreSQL and keeps the answer for 30 seconds.
- The key is `availability:v{version}:{checkIn}:{checkOut}`. The version lives in `availability:version`.
- Every successful booking and every cancellation adds 1 to the version. Old keys are no longer read and expire on their own.
- Only room numbers are cached. Room types come from the rooms list the app already holds.
- `GET /stats` reports dbQueries, cacheHits and cacheMisses so the effect can be measured (P08).

## Alternatives considered
- No cache: simple and always correct, but every search costs one query per room (2,000 queries for 1,000 searches of 2 rooms).
- Delete the affected keys on booking: correct for one date range, but a booking must know every date range it touches. The version number does this with one write.
- A TTL only, no invalidation: a room booked a second ago can still be listed for up to 30 seconds. Acceptable for a search, but the version gives fresher answers at the cost of one write per booking.
- Cache the booking check too: rejected. The booking would then trust a copy, which is how double booking returns.

## Consequences
+ Repeated searches are served from memory; the 1,000-search run needs one miss per version.
+ A booking or cancellation takes effect in the next search, not after the TTL.
- Every booking clears the cache for all dates at once (a version is global). Under heavy booking traffic the cache hit rate falls.
- A search that started before a booking can write its old answer to the new version after the booking has raised it. That answer then stays for at most 30 seconds. The booking itself is still safe, because it reads PostgreSQL.
- Redis is one more service to run, monitor and back up. If Redis is down the search must still work (not yet tested: it fails in P08).

## Revisit when
- The measured p95 or hit rate in docs/cache-experiment.md misses the S1 target.
- One popular date range becomes a hot key, or bookings make the global version change too often (P09 and P19 look at this).
