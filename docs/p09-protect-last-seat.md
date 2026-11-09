# P09 · Protect the last seat: hotel room R7 on 12–14 November

Brief: one room, two guests asking for the same nights at the same moment. The repair must never
let two Confirmed reservations share a night (R3), and no guest may get a crash instead of an answer.

## 1. Interleaving trace (before the repair)
Both requests run inside the app's unit of work: one transaction per request.

| Step | Maya's request | Omar's request | Database |
|---|---|---|---|
| 1 | checks R7 for 12–14: no overlap | checks R7 for 12–14: no overlap | nothing saved yet |
| 2 | waits (demo pause, 0.05 s) | waits (demo pause, 0.05 s) | nothing saved yet |
| 3 | `count()` = 0, so id = R101; INSERT R101 | `count()` = 0, so id = R101; INSERT R101 | the second INSERT waits for the first |
| 4 | COMMIT | the INSERT fails: duplicate key R101 | one row, R101 |

Cause: the check (step 1) and the save (step 3) are two separate steps. Both checks see an empty room.
The id is also made from a count, so both requests try the same id.

## 2. Three repairs compared
| Repair | How it protects the night | Trade-off |
|---|---|---|
| Atomic conditional update | one statement changes the room only if it is still free | needs a counter per room; does not fit a date range well |
| Optimistic version check | the room has a version; a booking fails if the version changed, then the request retries | needs a version column and a retry loop; retries under load |
| Short row lock (chosen) | the second request waits until the first commits, then sees its reservation | simple; waits under load; only protects requests that go through this lock |

Chosen: a transaction-level PostgreSQL advisory lock per room, taken before the overlap check
(`PostgresReservationStore.lock_room`, `pg_advisory_xact_lock`). It is released at COMMIT, so the check
and the save run as one step for that room. It needs no table change, and the Reservations module
owns it (it does not query the rooms table).

Stronger option for later (not built here): an exclusion constraint, `EXCLUDE USING gist (room WITH =,
daterange(check_in, check_out) WITH &&) WHERE (status = 'Confirmed')`. The database then refuses any
overlap, even from other applications. It is the best guard for R3, and I recommend it for P17 and beyond.

## 3. Evidence (executed, not simulated)
`race_check.py`: 100 pairs on PostgreSQL 18.6 (the same major version as the compose file), each pair starts
from an empty reservations table, both requests start at the same moment, with the same 0.05 s demo pause.

| Mode | Pairs | Double bookings | Outcomes |
|---|---|---|---|
| No lock (the bug) | 100 | 0 | 100 × one Accepted R101, one `IntegrityError` (the second request crashes) |
| Room lock (the repair) | 100 | 0 | 100 × one Accepted R101, one Unavailable (a clean 409) |

What this shows:
- The database never saved two rows for R7 in either mode, but without the lock this protection is accidental: the
  count-based id makes both requests write R101, and the primary key refuses the second one. The guest gets a crash
  (`IntegrityError`), which the API does not map to an HTTP answer. The lock gives the correct answer, Unavailable.
- The in-memory race (`python main.py --race`, P03/P04) still shows a real double booking, because a Python list has no
  lock to take. That demo is kept on purpose: it shows why a Python lock is not the fix.

## 4. Invariant protected
R3: for one room, no two Confirmed reservations share a night. S2 (quality scenarios): exactly one of each
pair gets the room, and the other gets Unavailable.

## 5. Limits (honest)
- Retry: not built. The lock removes the need for a retry in this design; the optimistic option would need one, and it is not tested here.
- The id is still made from a count. The lock makes that safe for one room; a sequence should replace it (later practice).
- The advisory lock key uses `hashtext`: two rooms could share a key (only extra waiting, never a wrong answer).
- The lock protects only this app's booking path. Another program writing to the table would bypass it. The exclusion constraint closes that gap.
- Not measured under many parallel guests: 100 pairs is a short test. S2's target is 0 of 100 pairs, which this run meets.
