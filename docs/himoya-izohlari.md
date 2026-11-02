# P03–P06: himoya uchun izohlar

Bu fayl har bir amaliyotda **nima qilindi** va **nega aynan shunday** qilinganini tushuntiradi.
P28 dagi individual himoyada har bir qarorni o'zingiz asoslab berishingiz kerak bo'ladi, shuning
uchun har bo'lim oxirida o'qituvchi berishi mumkin bo'lgan savollar va qisqa javoblar bor.

---

## P03 · UML: koddan oldin dizayn

**Nima qilindi:** `docs/diagrams.drawio` ga 5 ta sahifa qo'shildi (Use cases, Classes, Sequence - book,
Sequence - cancel, Activity - book) va `design-notes.md` ga uchta bo'lim yozildi.

**Asosiy g'oya:** har bir diagramma bitta savolga javob beradi.

| Diagramma | Qaysi savolga javob beradi | Koddagi aksi |
|---|---|---|
| Use cases | Kim va nima uchun foydalanadi? | 4 ta maqsad → `find_free_rooms`, `reserve`, `find`, `cancel` |
| Classes | Qaysi klass nimani saqlaydi va nima qiladi? | Har bir quti → bitta klass |
| Sequence | Kim kimni qaysi tartibda chaqiradi? | `reserve()` ichidagi qadamlar tartibi |
| Activity | Qayerda qaror qabul qilinadi? | `reserve()` boshidagi ikkita `if` |

**Muhim nozikliklar:**
- **Kompozitsiya va assotsiatsiya farqi.** `Reservation ◆── DateRange` kompozitsiya, chunki R101 ning
  sanalari faqat R101 ga tegishli. `Reservation ── Room` esa oddiy assotsiatsiya, chunki R7 xonasi bron
  yaratilishidan oldin ham, keyin ham mavjud bo'ladi.
- **"Reservation Room dan meros oladi" — bu xato.** Meros "X — bu Y ning bir turi" degani. Bron esa xonaning
  bir turi emas, u xonaga *ishora qiladi*.
- **Half-open interval.** `check_in < other.check_out and other.check_in < self.check_out` sharti
  ishlatiladi. Shuning uchun 12–14 va 14–16 kesishmaydi: Maya 14-kuni ertalab chiqib ketadi.

**Ehtimoliy savollar:**
- *Nega `has_overlap` `Reservation` da emas, `ReservationStore` da?* Chunki bitta bron faqat o'zini biladi,
  xonaning barcha bronlarini esa faqat store ko'ra oladi.
- *Nega bekor qilishda bron o'chirilmaydi?* Tarix saqlanib qolishi uchun. Holat Cancelled ga o'zgaradi
  va bron endi xonani band qilmaydi (R4).

---

## P04 · SOLID bilan refaktoring (oldin bajarilgan)

Bu amaliyot oldin bajarilib, push qilingan: kod modullarga ajratilgan, `NotificationSender` va
`ReservationStore` protokollari kiritilgan, testlar soni 6 tadan 8 taga yetgan. Bu safar unga
o'zgartirish kiritilmadi.

---

## P05 · Bounded context'lar (faqat dizayn)

**Nima qilindi:** `docs/quality-scenarios.md`, `docs/contexts.md` va draw.io dagi "Context map" sahifasi.
Kod o'zgartirilmadi.

**Quality scenario nima uchun kerak?** "Tez ishlasin" degan istakni tekshirib bo'lmaydi.
"200 ta qidiruvning p95 ko'rsatkichi ≤ 1 soniya" degan talabni esa tekshirsa bo'ladi.
Har bir ssenariy 7 qatordan iborat: source, stimulus, environment, artifact, response, measure va checked in.

**p95 ni nega o'rtacha qiymat o'rniga olamiz?** 99 ta so'rov 10 ms da va bittasi 30 soniyada javob bersa,
o'rtacha qiymat yaxshi ko'rinadi, lekin bitta mehmon 30 soniya kutib qoladi. p95 esa eng sekin 5% dan
tashqari hamma so'rovlar qanchalik tez ekanini ko'rsatadi.

**Qoida egasini qanday topamiz:** qoida qaysi ma'lumotlarni o'qiydi va o'sha ma'lumotlarning hammasini
qaysi kontekst saqlaydi — o'sha kontekst qoidaning egasi bo'ladi. Masalan, "bitta xonada bitta kechaga ikkita
Confirmed bron bo'lmasin" qoidasi xonaning barcha bronlarini o'qiydi. Ularni Reservations saqlaydi,
demak egasi Reservations.

**"Bir so'z — turli ma'no" nega muhim:** `Status` so'zi Reservations da Confirmed/Cancelled, Payments da
Paid/Declined, Notifications da esa Sent/Failed degan ma'noni bildiradi. Agar hammasi bitta umumiy maydonda
saqlansa, muvaffaqiyatsiz yuborilgan SMS Maya ning bronini "Failed" holatiga o'tkazib qo'yishi mumkin edi.
Bu R6 qoidasini buzadi.

**Context map'dagi o'qlar:**
- **To'liq chiziq** — savol. Reservations javobni kutadi (Rooms ga "qaysi xonalar bor?",
  P17 dan boshlab Payments ga "depozit ol").
- **Yashil nuqtali chiziq** — hodisa (event). `ReservationConfirmed` allaqachon sodir bo'lgan,
  Reservations hech kimni kutmaydi.
- Barcha o'qlar Reservations dan chiqadi va hech biri unga qaytmaydi. P06 dagi 3-qoida aynan shuni tekshiradi.

**Ehtimoliy savol:** *Nega Notifications ga butun `Reservation` emas, faqat 5 ta maydon yuboriladi?*
Javob: qabul qiluvchiga faqat kerakli narsa beriladi. Shunda Notifications Reservations ning ichki
ma'lumotlariga bog'lanib qolmaydi va kelajakda bu xabarni RabbitMQ orqali yuborish oson bo'ladi (P15).

---

## P06 · Modular monolith

**Nima qilindi:** kod 4 ta paketga ko'chirildi (`rooms`, `reservations`, `payments`, `notifications`).
Har birida ommaviy kontrakt (`__init__.py`) va ichki kod (`internal.py`) bor. Shuningdek
`pyproject.toml` da 3 ta import-linter qoidasi, ADR-001 va draw.io dagi "Modules" sahifasi qo'shildi.

**Isbot: hech narsa buzilmadi** (refaktoringning asosiy sharti):
- 8 ta test o'tadi va `lint-imports` natijasi: `Contracts: 3 kept, 0 broken`.
- Demo chiqishi oldingi bilan `diff` orqali solishtirildi — bir xil.
- Race hali ham double booking qiladi. Bu kutilgan natija: refaktoring xulq-atvorni o'zgartirmaydi.

**Nega aynan shu tartibda ko'chirildi?** Avval Rooms va Notifications ko'chirildi, chunki ular hech kimga
bog'liq emas. Keyin Reservations ko'chirildi, chunki u ikkalasiga bog'liq. Shu tartib tufayli har bir
qadamdan keyin kod ishlayotgan holatda qoldi.

**Dependency circle va undan qochish:** P04 da `send_confirmation(reservation)` butun `Reservation` ni
qabul qilardi. Bu Notifications → Reservations bog'liqligini yaratardi, Reservations esa allaqachon
Notifications ga bog'liq edi, ya'ni aylana hosil bo'lardi. Endi Notifications o'zining `Confirmation`
klassini e'lon qiladi va bog'liqlik faqat bir tomonga yo'nalgan.

**Arxitektura testining oddiy testdan farqi:** oddiy test ilova *nima qilishini* tekshiradi.
Arxitektura testi esa kod *qanday bog'langanini* (importlar grafini) tekshiradi. Ataylab buzib ko'rilganda
8 ta xulq testi yashil qoldi, faqat import-linter qizil bo'ldi. Ya'ni bu tekshiruv oddiy testlar
ko'ra olmaydigan muammoni ushlaydi.

**Wiring (`main.py`):** ichki klasslarni nomlashi mumkin bo'lgan yagona ilova fayli. P07 da PostgreSQL
store qo'shilganda BookingService o'zgarmaydi, faqat `main.py` dagi bitta qator o'zgaradi.
Bu Dependency Inversion tamoyilining amaldagi ko'rinishi.

**Ehtimoliy savollar:**
- *Nega microservice emas?* Jamoa kichik, alohida release yoki scaling ehtiyoji hali yo'q.
  Microservice tarmoq xatolari, retry, ko'proq deploy va monitoring olib keladi (ADR-001 ga qarang).
  Bu qaror o'lchangan ehtiyoj paydo bo'lganda qayta ko'rib chiqiladi.
- *Python `internal.py` ni import qilishni taqiqlamaydi-ku?* To'g'ri. Python da haqiqiy "private" modul yo'q,
  shuning uchun chegarani tilning o'zi emas, `lint-imports` tekshiruvi ushlab turadi (P25 dan CI da ham).

---

## "Ishlaydi" va "production'ga tayyor" o'rtasidagi farq (o'zingiz uchun)

Kurs keyingi amaliyotlarda quyidagilarni tuzatadi. Ular hozircha ataylab qoldirilgan, lekin himoyada
ularni bilishingizni ko'rsatish foydali:
- **Race condition** (`check-then-act`): `has_overlap` va `save` o'rtasida boshqa so'rov kirib qolishi mumkin.
  `threading.Lock` yetarli emas, chunki u faqat bitta jarayon ichida ishlaydi. Haqiqiy yechim ma'lumotlar
  bazasi darajasida: PostgreSQL `EXCLUDE USING gist` constraint yoki `SELECT ... FOR UPDATE` (P09).
- **ID generatsiyasi** `101 + count()` ko'rinishida. Bir vaqtdagi so'rovlarda takroriy ID paydo bo'ladi.
  Bazada sequence yoki UUID kerak.
- **`except Exception`** juda keng. Faqat yetkazib berish xatolarini ushlash, ularni log qilish va
  xabarni retry/outbox orqali qayta yuborish kerak (P10, P17).
