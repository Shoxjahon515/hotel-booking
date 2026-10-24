# P03 design notes

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
