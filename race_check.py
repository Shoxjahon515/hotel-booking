"""P09 check on PostgreSQL: two guests book R7 for 12-14 Nov at the same moment, PAIRS times.

Start PostgreSQL first (docker compose up -d, or any server with db/init.sql loaded).
    python race_check.py            -> the repaired code: the room lock is taken
    python race_check.py --no-lock  -> the same code with the lock switched off (the bug)
Each pair starts from an empty reservations table. The demo pause (slow_step_seconds) is the same as in P03/P04.
"""
from __future__ import annotations

import sys
import threading
from collections import Counter
from datetime import date

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from hotel_booking.notifications.internal import EmailNotificationSender
from hotel_booking.reservations import BookingService, DateRange, Guest
from hotel_booking.reservations.internal import PostgresReservationStore
from hotel_booking.rooms import Room

PAIRS = 100
ENGINE = create_engine("postgresql+psycopg://hotel:hotel@localhost:5432/hotel")
R7 = Room("R7", "Standard")
STAY = DateRange(date(2026, 11, 12), date(2026, 11, 14))
MAYA = Guest("Maya", "maya@example.com")
OMAR = Guest("Omar", "omar@example.com")


class NoLockStore(PostgresReservationStore):
    def lock_room(self, room: Room) -> None:
        pass  # the bug: nothing stops the two checks from running together


def one_pair(store_class) -> tuple[str, str, int]:
    with Session(ENGINE) as session:
        session.execute(text("DELETE FROM reservations"))
        session.commit()
    barrier = threading.Barrier(2)
    outcomes: dict[str, str] = {}

    def request(name: str, guest: Guest) -> None:
        try:
            with Session(ENGINE) as session:
                store = store_class(session, [R7])
                service = BookingService([R7], store, EmailNotificationSender(), slow_step_seconds=0.05)
                barrier.wait()
                outcomes[name] = str(service.reserve(guest, R7, STAY))
                store.save_changes()
        except Exception as error:  # the database refused a request: not an answer the guest sees
            outcomes[name] = f"error: {type(error).__name__}"

    threads = [threading.Thread(target=request, args=("Maya", MAYA)), threading.Thread(target=request, args=("Omar", OMAR))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    with Session(ENGINE) as session:
        confirmed = session.scalar(text(
            "SELECT count(*) FROM reservations WHERE room = 'R7' AND status = 'Confirmed' "
            "AND check_in < DATE '2026-11-14' AND check_out > DATE '2026-11-12'"))
    return outcomes["Maya"], outcomes["Omar"], confirmed


def main() -> None:
    store_class = NoLockStore if "--no-lock" in sys.argv else PostgresReservationStore
    print("mode:", "NO LOCK (bug)" if store_class is NoLockStore else "room lock (repair)")
    results = Counter()
    double_bookings = 0
    for _ in range(PAIRS):
        maya, omar, confirmed = one_pair(store_class)
        results[(maya, omar)] += 1
        double_bookings += confirmed > 1
    print(f"pairs: {PAIRS}")
    print(f"double bookings (2 confirmed rows for R7): {double_bookings}")
    for (maya, omar), count in sorted(results.items()):
        print(f"  Maya: {maya:<28} Omar: {omar:<28} x{count}")


if __name__ == "__main__":
    main()
