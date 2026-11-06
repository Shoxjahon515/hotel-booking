# Mehmonxona bron qilish · ASDA kurs loyihasi (23-309 SW)

[English](README.en.md) · **O'zbekcha**

Advanced Software Design & Architecture amaliyotlari davomida qurilayotgan mehmonxona bron qilish ilovasi.
Hozirgi holat: **P07**. Bu to'rtta moduldan (Rooms, Reservations, Payments, Notifications) iborat
modular monolith. Ilova http://localhost:5080 dagi HTTP API orqali ishlaydi, xonalar va bronlar
PostgreSQL'da saqlanadi.

## Ishga tushirish

Python 3.10 yoki undan yangi versiya va Docker Desktop kerak.

```text
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt

docker compose up -d             # R7 va R8 xonalari bilan PostgreSQL (db/init.sql)
python main.py                   # http://localhost:5080 dagi API (shartnoma: /openapi.yaml)
python main.py --demo            # to'qqiz qatorli demo, ma'lumotlar ro'yxatlarda
python main.py --race            # ikki mehmon R7 ni bir vaqtda bron qiladi (P09 gacha double booking bo'ladi)
```

Tekshiruvlar: 12 ta test (8 ta xulq + 4 ta API) va `pyproject.toml` dagi uchta modul chegarasi.

```text
python -m unittest -v
lint-imports                     # kutilgan natija: Contracts: 3 kept, 0 broken.
```

Bazani `docker compose down` bilan to'xtating (`-v` ni faqat ma'lumotlarni o'chirmoqchi bo'lsangiz qo'shing).

## Tuzilishi

```text
hotel_booking/
├── rooms/           Room, RoomCatalog                | ichki: InMemory/PostgresRoomCatalog
├── reservations/    BookingService, bron qoidasi     | ichki: InMemory/PostgresReservationStore
├── payments/        PaymentStatus, PaymentService    | ichki: SimulatedPaymentService
├── notifications/   Confirmation, NotificationSender | ichki: Email/Sms yuboruvchilar
└── api.py           uchta HTTP endpoint, to'rtta moduldan tashqarida
main.py              wiring: ichki kodni nomlaydigan yagona ilova fayli
db/init.sql          rooms va reservations jadvallari (har modulga bittadan, foreign key yo'q)
```

## Hujjatlar

| Fayl | Amaliyot |
|---|---|
| `docs/requirements.md` | P03: R1–R6 talablari, tekshiruvlari va isbot qatorlari |
| `docs/design-notes.md` | P03, P04, P06 va P07 bo'yicha qaydlar |
| `docs/diagrams.drawio` | Use cases, Classes, Sequence - book/cancel, Activity - book (P03); Classes - after (P04); Context map (P05); Modules (P06) |
| `docs/quality-scenarios.md` | P05: manfaatdor tomonlar va S1–S6 ssenariylari |
| `docs/contexts.md` | P05: so'zlar, to'rtta kontekst, qoida egalari, har bir chegaradan nima o'tadi |
| `docs/adr-001-modular-monolith.md` | P06: arxitektura qarori |
| `docs/capacity.md` | P07: sig'im (capacity) hisobi |
| `docs/openapi.yaml` | P07: API shartnomasi (uchta operatsiya, beshta xato nomi) |
| `docs/api-check.md` | P07: PostgreSQL'ga yuborilgan yettita so'rov va restart tekshiruvi |
| `docs/himoya-izohlari.md` | Individual himoya uchun o'zbekcha izohlar |
