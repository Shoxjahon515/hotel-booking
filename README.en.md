# Hotel booking · ASDA course project (23-309 SW)

**English** · [O'zbekcha](README.md)

The hotel booking app built across the Advanced Software Design & Architecture practices.
Current state: **P07**, a modular monolith with four modules (Rooms, Reservations, Payments, Notifications)
behind an HTTP API on http://localhost:5080, with its rooms and reservations in PostgreSQL.

## Run

Python 3.10 or newer and Docker Desktop.

```text
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt

docker compose up -d             # PostgreSQL with rooms R7 and R8 (db/init.sql)
python main.py                   # the API on http://localhost:5080 (contract: /openapi.yaml)
python main.py --demo            # the nine-line demo, with the data in lists
python main.py --race            # two guests book R7 at the same moment (still double-books until P09)
```

Checks: 12 tests (8 behaviour + 4 API) and the three module borders from `pyproject.toml`.

```text
python -m unittest -v
lint-imports                     # expected: Contracts: 3 kept, 0 broken.
```

Stop the database with `docker compose down` (add `-v` only to delete its data).

## Layout

```text
hotel_booking/
├── rooms/           Room, RoomCatalog              | internal: InMemory/PostgresRoomCatalog
├── reservations/    BookingService, the booking rule | internal: InMemory/PostgresReservationStore
├── payments/        PaymentStatus, PaymentService  | internal: SimulatedPaymentService
├── notifications/   Confirmation, NotificationSender | internal: Email/Sms senders
└── api.py           the three HTTP endpoints, outside the four modules
main.py              the wiring: the only app file that names internal code
db/init.sql          the rooms and reservations tables (one per module, no foreign key)
```

## Docs

| File | Practice |
|---|---|
| `docs/requirements.md` | P03: R1–R6 with checks and proof lines |
| `docs/design-notes.md` | P03, P04, P06 and P07 notes |
| `docs/diagrams.drawio` | Use cases, Classes, Sequence - book/cancel, Activity - book (P03); Classes - after (P04); Context map (P05); Modules (P06) |
| `docs/quality-scenarios.md` | P05: stakeholders and S1–S6 |
| `docs/contexts.md` | P05: words, four contexts, rule owners, what crosses each border |
| `docs/adr-001-modular-monolith.md` | P06: the architecture decision |
| `docs/capacity.md` | P07: the capacity estimate |
| `docs/openapi.yaml` | P07: the API contract (three operations, five error titles) |
| `docs/api-check.md` | P07: seven requests against PostgreSQL and the restart check |
| `docs/himoya-izohlari.md` | Explanations in Uzbek for the individual defense |
