# P03 design notes

## Why design before code
Low-level design decides which classes the app has, what each one keeps (its data) and does
(its methods), and who calls whom. For example: the overlap rule lives only in DateRange,
Reservation knows its own status, and BookingService runs check → save → email → answer in
that order. Deciding this in a diagram is cheap; changing it later in the code is expensive,
and a rule typed in two places (website and reception desk) drifts apart.

## Where the methods live
- cancel() lives in Reservation, because cancelling changes only the reservation's own status;
  nothing is deleted, so R101 stays in the store as Cancelled and the history is kept.
- has_overlap() lives in ReservationStore, because only the store can see all the reservations
  of a room at once; one Reservation only knows about itself.

## Activity traces
- Omar, R7, 13–15 Nov (Maya has 12–14): Check-out after check-in? Yes. A Confirmed booking
  shares a night? Yes, the 13th. Ends at "Unavailable · save nothing".
- Nora, R7, 14–16 Nov (Maya has 12–14): Check-out after check-in? Yes. A Confirmed booking
  shares a night? No: Maya leaves on the 14th, so 12 < 16 but 14 < 14 is false. Save the
  reservation as Confirmed → send the email → ends at "Accepted R102".
- Omar, R8, 15–15 Nov: Check-out after check-in? No (15 is not after 15). Ends at
  "InvalidDates · save nothing"; the second question is never asked.

## The race
Prediction: R7 will have 2 Confirmed reservations for 12–14 November.
What happened: both Maya and Omar got Accepted, so R7 is double-booked.
The problem appears between `store.has_overlap(...)` (check) and `store.save(...)` (act):
both requests checked an empty store before either one saved.
Why a Python lock is not the real fix: threading.Lock only protects one process. In production
the app runs in several workers or servers, so the rule "one guest per room per night" must be
protected by the database (P09: a PostgreSQL exclusion constraint or SELECT ... FOR UPDATE).

# P04 design notes

## Refactoring
Refactoring means I reorganise the code — rename classes, move them into separate files,
and make BookingService ask for interfaces instead of concrete classes — while the guest
gets exactly the same answers as before. If any answer changes, it was not a refactoring
but a bug fix or a new feature, and those are done as separate steps.

Must stay the same:
- The tests from Step 2: all 6 still pass after every move.
- The demo output: the same nine lines as in P03.
- The race demo: still "Double booking!" (refactoring does not fix bugs).

## What our code breaks
- BookingService asks for exactly ReservationStore (D: dependency inversion).
  In P07 we would have to edit BookingService just to use a database.
- BookingService asks for exactly EmailSender (D and O: open/closed).
  Adding SMS confirmations means opening and editing BookingService,
  and tests cannot make the email fail, so we cannot prove a failed email keeps the booking.
- All nine classes live in one file, hotel_booking.py (S: single responsibility).
  Every change touches the same file and code is hard to find.
- Noted, not fixed: the demo pause (slow_step_seconds) sits inside reserve().
  It stays on purpose so the race can still be shown; P09 removes the race in the database.

## Target design
- BookingService depends on two protocols: ReservationStore and NotificationSender.
- InMemoryReservationStore implements ReservationStore (the P03 list store, renamed).
- EmailNotificationSender and SmsNotificationSender implement NotificationSender.
- FakeNotificationSender (tests only) implements NotificationSender.
- main.py is the only place that chooses the real store and sender.
See diagrams.drawio, page "Classes - after".

## Proof
Run on 24 October 2026, Python 3, from the hotel-booking folder.
- Tests: `python3 -m unittest -v` → Ran 8 tests ... OK
  (the 6 Step 2 tests stayed green after every move; R6 and SMS added 2 more).
- Demo: `python3 main.py` → the same nine lines as P03, ending with "Confirmation emails sent: 2".
- Race: `python3 main.py --race` → "Confirmed reservations for R7 on 12-14 Nov: 2",
  "Double booking!" — unchanged, as expected for a pure refactoring.

## Benefit (Step 7)
- A fake sender lets the tests check the exact ids (R101, R102) and force a failure.
- R6 was added by changing only reserve(); the test was written first and failed (red), then passed.
- SMS was added as one new class; BookingService was not edited (O in SOLID).

## Limitations (noted for later practices)
- The race is still there: check and save are two separate steps (fixed in P09).
- Reservation ids come from `101 + count()`: unsafe under concurrency.
- R6 catches every Exception; a real system would catch only delivery errors, log them and retry the message.

# P06 design notes

## Before
Run on 2 November 2026, Python 3, from the hotel-booking folder, before moving any code.
- Tests: `python -m unittest -v` → Ran 8 tests ... OK
- Demo: `python main.py` → the nine P03/P04 lines, ending with "Confirmation emails sent: 2".
- Race: `python main.py --race` → "Confirmed reservations for R7 on 12-14 Nov: 2", "Double booking!".

## Modules

| Module | Public contract (others may use) | Internal code (only the module, the wiring and the tests) |
|---|---|---|
| Rooms | Room, the room catalog promise (RoomCatalog) | InMemoryRoomCatalog |
| Reservations | BookingService, BookingResult, Reservation, DateRange, Guest, ReservationStatus, the store promise (ReservationStore) | InMemoryReservationStore |
| Payments | PaymentStatus, the payment service promise (PaymentService) | SimulatedPaymentService |
| Notifications | Confirmation, the notification sender promise (NotificationSender) | EmailNotificationSender, SmsNotificationSender |

Order of the moves: Rooms and Notifications first (they need no other module), then
Reservations (it needs both), then the new Payments contract. The tests stayed green after
every move. The only change inside BookingService: reserve() now sends Notifications' own
Confirmation (the five fields from contexts.md "Between contexts") instead of the whole
Reservation, so Notifications no longer depends on Reservations and there is no circle.

## Architecture rules
1. Reservations uses only the public contracts of other modules: BookingService may use the
   Notifications contract, never the email sender.
2. Rooms does not depend on any other module: it knows nothing about reservations, money or messages.
3. Payments and Notifications do not depend on Reservations: the arrows point one way, from
   Reservations outwards, so there is never a dependency circle.
They live in pyproject.toml and run with `lint-imports` (import-linter).

## Broken on purpose
I added `from hotel_booking.notifications.internal import EmailNotificationSender` to
hotel_booking/reservations/booking.py. The 8 tests still passed; lint-imports failed rule 1,
"Reservations uses only the public contracts of other modules", naming
`hotel_booking.reservations.booking -> hotel_booking.notifications.internal (l.8)`.
"Contracts: 2 kept, 1 broken." I removed the line and all checks were green again.

## After
- Tests: `python -m unittest -v` → Ran 8 tests ... OK; `lint-imports` → Contracts: 3 kept, 0 broken.
- Demo: `python main.py` → the same nine lines as in "Before" (compared with diff: identical).
- Race: `python main.py --race` → still "Double booking!": moving code into modules does not
  fix the race; P09 fixes it in the database.

# P07 design notes

## API decisions
- Order of the free rooms: text order of the room number, so R10 comes before R7. The "after"
  cursor compares text the same way, so every client knows where the next page starts.
- What a client compares: the problem's title (Unavailable, InvalidDates, UnknownRoom,
  InvalidRequest, NotFound). detail is a sentence for people and may change.
- Room type: catalog data from the rooms table (Standard, Deluxe), not a fixed list in the
  contract; a new type needs no API change.

## API tests
- GET /rooms/availability?checkIn=2026-11-12&checkOut=2026-11-14 → 200 with R7 and R8, next null.
- POST /reservations Maya R7 12–14 Nov → 201 {"id":"R101",...}; then Omar R7 13–15 Nov → 409 Unavailable.
- POST /reservations with checkIn = checkOut (15–15 Nov) → 400 InvalidDates as application/problem+json.
- POST Maya, then DELETE /reservations/R101 → 204; DELETE again → 404 NotFound.
Broken on purpose: changing the expected 409 to 201 made the second test fail ("201 != 409");
changed back, all green.

## After
- Checks: `python -m unittest -v` → Ran 12 tests ... OK (8 behaviour + 4 API);
  `lint-imports` → Contracts: 3 kept, 0 broken. `--demo` prints the same nine lines; `--race`
  still double-books (P09).
- Seven requests against PostgreSQL: all seven ✓ (docs/api-check.md).
- Restart check: after stopping and starting the app, R7 is still booked for 12–14 Nov;
  the reservations table keeps R101 (Cancelled) and R102 (Confirmed).
- requirements.txt: the reference pins sqlalchemy==2.1.6, which needs Python 3.11+, while the
  course allows Python 3.10. An environment marker installs SQLAlchemy 2.0.55 on Python 3.10;
  the 12 tests and all seven PostgreSQL requests were checked with both versions.
