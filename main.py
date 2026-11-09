"""P08 - Hotel booking: the P07 API with a Redis cache for the free-room search.

python main.py          -> the API on http://localhost:5080 (first: docker compose up -d)
python main.py --demo   -> the P06 demo, with the data in lists
python main.py --race   -> two guests book the same room at the same moment
"""
from __future__ import annotations

import os
import sys
import threading
import time
from contextlib import contextmanager
from datetime import date

import redis
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from hotel_booking.api import create_app
from hotel_booking.availability import AvailabilityCache, NoCache, RedisCache
from hotel_booking.notifications.internal import EmailNotificationSender
from hotel_booking.reservations import BookingResult, BookingService, DateRange, Guest
from hotel_booking.reservations.internal import InMemoryReservationStore, PostgresReservationStore
from hotel_booking.rooms import Room
from hotel_booking.rooms.internal import InMemoryRoomCatalog, PostgresRoomCatalog
from hotel_booking.stats import Stats

R7 = Room("R7", "Standard")
R8 = Room("R8", "Deluxe")
MAYA = Guest("Maya", "maya@example.com")
OMAR = Guest("Omar", "omar@example.com")
NORA = Guest("Nora", "nora@example.com")

# The wiring: the only app code that imports the internal modules.
CATALOG = InMemoryRoomCatalog([R7, R8])


def nov(check_in: int, check_out: int) -> DateRange:
    return DateRange(date(2026, 11, check_in), date(2026, 11, check_out))


def names(rooms: list[Room]) -> str:
    return ", ".join(room.number for room in rooms)


def run_demo() -> None:
    store = InMemoryReservationStore()
    email = EmailNotificationSender()
    service = BookingService(CATALOG.all(), store, email)

    print(f"Free rooms 12-14 Nov: {names(service.find_free_rooms(nov(12, 14)))}")
    print(f"Maya books R7 12-14 Nov: {service.reserve(MAYA, R7, nov(12, 14))}")
    print(f"Omar books R7 13-15 Nov: {service.reserve(OMAR, R7, nov(13, 15))}")
    print(f"Nora books R7 14-16 Nov: {service.reserve(NORA, R7, nov(14, 16))}")
    print(f"Omar books R8 15-15 Nov: {service.reserve(OMAR, R8, nov(15, 15))}")
    print(f"Free rooms 12-14 Nov: {names(service.find_free_rooms(nov(12, 14)))}")
    print(f"Maya cancels R101: {service.cancel('R101')}")
    print(f"Free rooms 12-14 Nov: {names(service.find_free_rooms(nov(12, 14)))}")
    print(f"Confirmation emails sent: {email.sent}")


def run_race() -> None:
    store = InMemoryReservationStore()
    # Each request now spends half a second between checking and saving.
    service = BookingService(CATALOG.all(), store, EmailNotificationSender(), slow_step_seconds=0.5)
    stay = nov(12, 14)
    results: dict[str, BookingResult] = {}

    print("Maya and Omar both book R7 for 12-14 Nov at the same moment...")
    maya_request = threading.Thread(target=lambda: results.update(Maya=service.reserve(MAYA, R7, stay)))
    omar_request = threading.Thread(target=lambda: results.update(Omar=service.reserve(OMAR, R7, stay)))
    maya_request.start()
    time.sleep(0.1)  # Omar clicks a moment after Maya
    omar_request.start()
    maya_request.join()
    omar_request.join()

    print(f"Maya: {results['Maya']}")
    print(f"Omar: {results['Omar']}")
    confirmed = store.count_confirmed(R7, stay)
    print(f"Confirmed reservations for R7 on 12-14 Nov: {confirmed}")
    print("Double booking! Both requests checked before either one saved."
          if confirmed > 1 else "Only one guest has R7.")


class CountingStore(PostgresReservationStore):
    """The PostgreSQL store, counting its queries for GET /stats."""

    def __init__(self, session: Session, rooms: list[Room], stats: Stats) -> None:
        super().__init__(session, rooms)
        self._stats = stats

    def has_overlap(self, room: Room, stay: DateRange) -> bool:
        self._stats.db_queries += 1
        return super().has_overlap(room, stay)


def run_api() -> None:
    # The wiring for the web app: PostgreSQL and Redis from docker-compose.yml.
    # HOTEL_DB_PORT is only needed if 5432 is taken; HOTEL_REDIS_URL only if Redis is not on localhost:6379.
    engine = create_engine(f"postgresql+psycopg://hotel:hotel@localhost:{os.getenv('HOTEL_DB_PORT', '5432')}/hotel")
    rooms = PostgresRoomCatalog(engine).all()
    email = EmailNotificationSender()
    stats = Stats()
    if os.getenv("HOTEL_CACHE") == "off":  # P08 baseline: every search asks PostgreSQL
        availability = AvailabilityCache(NoCache(), stats)
    else:
        redis_client = redis.Redis.from_url(os.getenv("HOTEL_REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
        availability = AvailabilityCache(RedisCache(redis_client), stats)

    @contextmanager
    def unit_of_work():
        # One request: a fresh store over its own session; save what changed at the end.
        with Session(engine) as session:
            store = CountingStore(session, rooms, stats)
            yield BookingService(rooms, store, email)
            store.save_changes()

    uvicorn.run(create_app(rooms, unit_of_work, availability, stats), host="localhost", port=5080)


if __name__ == "__main__":
    if "--race" in sys.argv:
        run_race()
    elif "--demo" in sys.argv:
        run_demo()
    else:
        run_api()
