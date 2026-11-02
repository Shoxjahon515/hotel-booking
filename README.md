# Hotel booking · ASDA course project (23-309 SW)

The hotel booking app built across the Advanced Software Design & Architecture practices.
Current state: **P06**, a modular monolith with four modules (Rooms, Reservations, Payments, Notifications).

## Run

Python 3.10 or newer; the app itself needs no packages.

```text
python -m unittest -v     # 8 behaviour tests
python main.py            # the nine-line demo
python main.py --race     # two guests book R7 at the same moment (still double-books until P09)
```

Architecture checks (the three module borders, defined in `pyproject.toml`):

```text
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install import-linter
lint-imports                     # expected: Contracts: 3 kept, 0 broken.
```

## Layout

```text
hotel_booking/
├── rooms/           Room, RoomCatalog              | internal: InMemoryRoomCatalog
├── reservations/    BookingService, the booking rule | internal: InMemoryReservationStore
├── payments/        PaymentStatus, PaymentService  | internal: SimulatedPaymentService
└── notifications/   Confirmation, NotificationSender | internal: Email/Sms senders
main.py              the wiring: the only app file that names internal code
```

## Docs

| File | Practice |
|---|---|
| `docs/requirements.md` | P03: R1–R6 with checks and proof lines |
| `docs/design-notes.md` | P03, P04 and P06 notes |
| `docs/diagrams.drawio` | Use cases, Classes, Sequence - book/cancel, Activity - book (P03); Classes - after (P04); Context map (P05); Modules (P06) |
| `docs/quality-scenarios.md` | P05: stakeholders and S1–S6 |
| `docs/contexts.md` | P05: words, four contexts, rule owners, what crosses each border |
| `docs/adr-001-modular-monolith.md` | P06: the architecture decision |
| `docs/himoya-izohlari.md` | Explanations in Uzbek for the individual defense |
