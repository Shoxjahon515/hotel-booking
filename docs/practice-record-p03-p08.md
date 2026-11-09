# Practice record: P03 to P08 (text only, no code)

Why this file exists: from P03 on, the course site has no worksheet for these practices. Each one is
recorded as files in this repository, plus the notes below. The site says P04 is evidence kept in
the project, not an online worksheet. Sources for each entry are named in brackets.
Partner names are not recorded here.

---

## English

### P03 · Hotel booking domain and UML workshop
- Requirements R1–R6 written with checks and proof lines: search, book, no clash, cancel, view, failed message (`docs/requirements.md`).
- Diagrams in draw.io: use cases, classes, sequence (book, cancel), activity (book) (`docs/diagrams.drawio`).
- Design notes: why `cancel()` belongs to `Reservation` and `has_overlap()` to the store; activity traces for Omar, Nora and the invalid date case (`docs/design-notes.md`).
- Race demo: prediction was 2 confirmed bookings for R7 on 12–14 Nov. Result: double booking, because both requests checked before either saved. A Python lock was rejected as the fix, since it protects only one process. The real fix belongs to the database (P09).
- Commit: `4039db1` (combined with P05 and P06).

### P04 · Refactor a reservation design
- Refactoring is defined as: same answers, better structure. Tests and demo output must stay the same. The race must still show (refactoring does not fix bugs) (`docs/design-notes.md`).
- Problems found: `BookingService` depended on concrete classes; adding SMS would mean editing it; all classes sat in one file.
- Target design: `BookingService` depends on two protocols, `ReservationStore` and `NotificationSender`. SMS was added as a new sender class.
- Evidence: the R6 test (a failed message keeps the booking) and the SMS sender test (scenario S5). Original project: `hotel-booking-P04.zip` in Downloads, first commits `57334f8` and `1d222ad` (24 Oct 2026).

### P05 · Hotel domain and context boundaries
- Glossary of the hotel: words, meanings and the names used in code (`docs/contexts.md`).
- Bounded contexts with the rules each one owns and what crosses each border. The Rooms context knows only which rooms exist and whether a room is out of service.
- Six quality scenarios, S1–S6, each with source, stimulus, artifact, response and a measure. S1 (search speed, p95 ≤ 1 s) and S6 (less energy per search) are later checked in P08 (`docs/quality-scenarios.md`).
- Context map diagram in draw.io.
- Commit: `4039db1`.

### P06 · Modular-monolith architecture review
- ADR-001: one app with four modules (Rooms, Reservations, Payments, Notifications). Each module has a public contract and internal code. Alternative rejected for now: separate services (`docs/adr-001-modular-monolith.md`).
- Code split into four modules, `main.py` as the only file that names internal code.
- Three architecture rules in `pyproject.toml`, checked with import-linter: all three kept (`lint-imports`).
- Modules diagram in draw.io.
- Commit: `4039db1`.

### P07 · Capacity and API design studio
- HTTP API with FastAPI: search, book and cancel endpoints, plus `/openapi.yaml` as the contract (`docs/openapi.yaml`).
- PostgreSQL 18 in Docker Compose. Reservations are kept in the database and survive a restart.
- Problem details (RFC 9457) for every error, and cursor pagination for search (`docs/api-check.md`).
- Capacity estimate with assumptions and calculations, labelled as estimates (`docs/capacity.md`).
- Seven requests were checked against PostgreSQL on 2 November 2026, all as expected, plus a restart check (`docs/api-check.md`).
- Commit: `6d5c5c7`.

### P08 · Cache and scale experiment (today, 8 November 2026)
- Redis 8 added to Docker Compose. Cache-aside for the free-room search, 30-second TTL, key with a version number (`docs/adr-002-cache-availability.md`).
- Booking and cancellation raise the version, so stale searches are no longer read. Bookings still check PostgreSQL.
- `GET /stats` counts database queries and cache hits and misses. `measure.py` runs 1,000 searches and prints average and p95.
- 14 unit tests pass; import-linter keeps 3 contracts.
- Not done yet: the measurements. The laptop has no Docker, so the server, Redis and PostgreSQL were not run. The results table in `docs/cache-experiment.md` is empty until the run is done.
- Commit: `2f3074a`. Not pushed yet.

---

## O'zbekcha

### P03 · Hotel booking domeni va UML workshopi
- R1–R6 talablari tekshiruv va isbot satrlari bilan yozilgan: qidiruv, bron, to'qnashuv yo'qligi, bekor qilish, ko'rish, xabar xatosi (`docs/requirements.md`).
- draw.io diagrammalari: use case, class, sequence (bron, bekor qilish), activity (bron) (`docs/diagrams.drawio`).
- Loyiha eslatmalari: nega `cancel()` `Reservation` da, `has_overlap()` esa store da turishi; Omar, Nora va noto'g'ri sana uchun faoliyat izlari (`docs/design-notes.md`).
- Poyga demosi: bashorat 12–14 noyabr uchun R7 da 2 ta tasdiqlangan bron edi. Natija: ikki bron, chunki ikkala so'rov ham saqlashdan oldin tekshirgan. Python lock tuzatish sifatida rad etildi, chunki u faqat bitta jarayonni himoya qiladi. Haqiqiy tuzatish ma'lumotlar bazasida bo'ladi (P09).
- Commit: `4039db1` (P05 va P06 bilan birga).

### P04 · Bron dizaynini refaktoring qilish
- Refaktoring ta'rifi: javoblar o'sha-o'sha, tuzilma yaxshiroq. Testlar va demo chiqishi o'zgarmasligi kerak. Poyga ko'rinib qolishi kerak, chunki refaktoring xatolarni tuzatmaydi (`docs/design-notes.md`).
- Topilgan muammolar: `BookingService` aniq klasslarga bog'liq edi, SMS qo'shish uchun uni tahrirlash kerak edi, barcha klasslar bitta faylda edi.
- Maqsadli dizayn: `BookingService` ikkita protokolga bog'liq, `ReservationStore` va `NotificationSender`. SMS yangi sender klassi sifatida qo'shildi.
- Dalil: R6 testi (xabar xato bersa ham bron saqlanadi) va SMS sender testi (S5 stsenariysi). Asl loyiha: Downloads'dagi `hotel-booking-P04.zip`, birinchi commitlar `57334f8` va `1d222ad` (2026-yil 24-oktabr).

### P05 · Hotel domeni va kontekst chegaralari
- Mehmonxona lug'ati: so'zlar, ma'nolari va kodda ishlatilgan nomlari (`docs/contexts.md`).
- Chegaralangan kontekstlar, har biri egalik qiladigan qoidalar va har bir chegaradan nima o'tishi. Rooms konteksti faqat qaysi xonalar mavjudligini va xona xizmatdan chiqarilganini biladi.
- Oltita sifat stsenariysi, S1–S6, har birida manba, stimul, artefakt, javob va o'lchov. S1 (qidiruv tezligi, p95 ≤ 1 soniya) va S6 (har bir qidiruvga kam energiya) P08 da qayta tekshiriladi (`docs/quality-scenarios.md`).
- draw.io da kontekst xaritasi diagrammasi.
- Commit: `4039db1`.

### P06 · Modulli monolit arxitektura ko'rib chiqish
- ADR-001: bitta ilova, to'rtta modul (Rooms, Reservations, Payments, Notifications). Har bir modulning ochiq shartnomasi va ichki kodi bor. Hozircha alohida servislar variant sifatida rad etilgan (`docs/adr-001-modular-monolith.md`).
- Kod to'rtta modulga bo'lingan, `main.py` ichki kodni nomlaydigan yagona fayl.
- `pyproject.toml` da uchta arxitektura qoidasi, import-linter bilan tekshirilgan: uchalasi ham o'tgan (`lint-imports`).
- draw.io da modullar diagrammasi.
- Commit: `4039db1`.

### P07 · Sig'im va API dizayn studiyasi
- FastAPI bilan HTTP API: qidiruv, bron va bekor qilish endpointlari, shartnoma sifatida `/openapi.yaml` (`docs/openapi.yaml`).
- Docker Compose da PostgreSQL 18. Bronlar ma'lumotlar bazasida saqlanadi va qayta ishga tushgandan keyin ham qoladi.
- Har bir xato uchun problem details (RFC 9457) va qidiruv uchun cursor pagination (`docs/api-check.md`).
- Taxminlar va hisob-kitoblar bilan sig'im bahosi, baho sifatida belgilangan (`docs/capacity.md`).
- 2026-yil 2-noyabrda PostgreSQL ga qarshi yettita so'rov tekshirilgan, hammasi kutilganidek, qayta ishga tushirish testi ham o'tgan (`docs/api-check.md`).
- Commit: `6d5c5c7`.

### P08 · Cache va masshtab tajribasi (bugun, 2026-yil 8-noyabr)
- Docker Compose ga Redis 8 qo'shildi. Bo'sh joy qidiruvi uchun cache-aside, 30 soniya TTL, versiya raqami bilan kalit (`docs/adr-002-cache-availability.md`).
- Bron va bekor qilish versiyani oshiradi, shuning uchun eskirgan qidiruv o'qilmaydi. Bronlar baribir PostgreSQL ni tekshiradi.
- `GET /stats` ma'lumotlar bazasi so'rovlarini, cache hit va miss sonini hisoblaydi. `measure.py` 1 000 ta qidiruv o'tkazib, o'rtacha va p95 ni chiqaradi.
- 14 ta unit test o'tdi; import-linter 3 ta shartnomani saqlaydi.
- Hali bajarilmagan: o'lchovlar. Noutbukda Docker yo'q, shuning uchun server, Redis va PostgreSQL ishga tushirilmagan. `docs/cache-experiment.md` dagi natijalar jadvali o'lchov o'tkazilguncha bo'sh.
- Commit: `2f3074a`. Hali push qilinmagan.
