# Worksheet record: P01 and P02 (text only, no code)

Source: the teaching site worksheets for group 23-309 SW (both already submitted, revision 3).
These records summarise what was done. The full answers stay on the site.
Partner names are not recorded anywhere in these worksheets.

---

## English

### P01 · Course introduction workshop and project baseline
Fictional brief: a concert organiser needs an app where customers see availability, book a ticket and check their booking. 20 tickets per concert, no numbered seats, one ticket per customer per concert, no payment in version one.

What was done:
- **Programming example:** explained `find_free_rooms(stay)` from the hotel-booking practice, and the `Reservation` object whose `cancel()` method enforces its own status rule.
- **SQL starting point:** a query that finds Alex's booking by email and concert. Email is used because names can repeat. The lookup returns 0 or 1 row because of the one-booking rule. A `UNIQUE (concert_id, customer_id)` constraint would guarantee that.
- **Computer starting point:** unsaved data lives in RAM and is lost when the app closes. A booking counts only after the database commits it.
- **Personal learning goal:** how to guarantee that concurrent Book clicks never exceed capacity, even on several servers.
- **Scope:** availability, booking and status check in version one. Payment, cancellation, waiting list and numbered seats are out.
- **Unresolved policies:** waiting list, cancellation rules, and what identifies a customer (email or account). Each has a named answerer.
- **Three functional needs:** availability (17 of 20 sold, "3 tickets left", no save), booking ("Booked, reference B-018", one new confirmed booking), status check (read only).
- **Booking rules:** capacity (never more than 20 confirmed) and one booking per customer per concert. Both must be enforced in the database, not only in an `if`. Sold-out and duplicate examples given.
- **Quality concerns:** correctness under concurrency (target 0 overbookings, proposed, not measured), accessibility for keyboard-only users, and response time on release day (target to agree).
- **Context sketch:** Customer, Ticket app, Organiser, Support and Email provider, with labelled messages. The Ticket app owns the booking data.
- **Five terms:** concert, capacity, confirmed booking, sold out, cancellation.
- **Team responsibilities:** the author drafted most parts and checked them against the brief. The partner's part is not recorded.
- **Tool-access checklist:** VS Code and Python available on macOS. Git was not yet checked at the time. Database tools were available.
- **Peer feedback:** a self-review. One sentence was rewritten from "must not sell more tickets than capacity" to a precise rule. Evidence label: proposed, not verified.
- **Individual reflection:** the capacity rule, the author's contribution, and an open question on where the rule should live when the app runs on several servers.

Status: submitted. Limitation: the concurrency rule is written but not yet tested against a real database.

### P02 · OS introduction, kernels and process lifecycle
Lab: a parent Python program starts a child program. The child waits for Enter, saves a small file and exits. The author ran it on macOS (Apple Silicon, Python 3.13) on 24 October 2026, around 12:15.

What was observed (own run):
- Child PID **15188**, parent PID **15169**. The child reported platform Darwin and did 8,460,407 loop iterations in 0.75 s.
- Timeline: created (Popen) → CPU work → blocked at `input()` → Enter pressed → file saved → exit with code 7 → parent's `wait()` returned.
- Changed code: `EXIT_CODE` from 7 to 3. Prediction: exit code 3 and `requested_exit_code=3` in the file. Actual: child PID 15347, parent PID 15343, exit code 3 and the file updated, as predicted. The parent then printed "unexpected child result" because it only accepts 7. This shows an unwritten contract between parent and child.

What was not observed (recorded honestly):
- `ps` was run with an example PID (12345) that the author typed by mistake. The child had already exited, so the output had only the header. **State, threads and memory (VSZ, RSS) were not measured.** The correct method was to keep the child waiting and run `ps -p <PID>` in a second terminal.

Concepts explained:
- `fork()` creates a copy of the parent. `exec` replaces the program in the child but keeps the PID. `wait` collects the exit code and removes the zombie.
- Windows has no `fork()`. `CreateProcess` creates the process and loads the program in one call.
- Ready and blocked are different: a blocked process waits for an event (here, the keypress).
- A saved file survives the process because the kernel and filesystem own it, not the process. A successful `write()` does not guarantee power-loss safety; that needs `fsync`.

Runtime decision (provisional): C#/.NET 10 for the future enrolment project, because it runs on macOS, Windows and Linux and the course starter uses it. Still to verify: installation on every team laptop, IDE support, and PostgreSQL driver support. Reconsider if the lecturer requires Java or a laptop cannot install .NET 10.

Status: submitted. Limitation: one run only; the process-state and memory fields are missing.

---

## O'zbekcha

### P01 · Kurs kirish workshopi va loyiha bazasi
Uydirma topshiriq: kichik konsert tashkilotchisiga mijozlar bo'sh joyni ko'radigan, chipta bron qiladigan va bronini tekshiradigan ilova kerak. Har bir konsertga 20 ta chipta, raqamlangan o'rindiqlar yo'q, har bir mijoz bir konsertga bitta chipta oladi, birinchi versiyada to'lov yo'q.

Bajarilgani:
- **Dasturlash misoli:** hotel-booking amaliyotidagi `find_free_rooms(stay)` funksiyasi va `Reservation` obyekti tushuntirildi. Obyektning `cancel()` metodi o'z holat qoidasini o'zi saqlaydi.
- **SQL boshlang'ich nuqtasi:** Alexning bronini email va konsert bo'yicha topadigan so'rov yozildi. Email tanlangan, chunki ismlar takrorlanishi mumkin. Bitta bron qoidasi tufayli natija 0 yoki 1 qator. `UNIQUE (concert_id, customer_id)` cheklovi buni kafolatlaydi.
- **Kompyuter boshlang'ich nuqtasi:** saqlanmagan ma'lumot RAM'da turadi va ilova yopilganda yo'qoladi. Bron faqat ma'lumotlar bazasi uni saqlagandan keyin hisobga o'tadi.
- **Shaxsiy o'quv maqsadi:** bir vaqtda Book bosilganda sig'imdan oshmaslikni, bir nechta serverda ham, qanday kafolatlash mumkinligi.
- **Doira:** birinchi versiyada bo'sh joy, bron va holatni tekshirish bor. To'lov, bekor qilish, kutish ro'yxati va raqamlangan o'rindiqlar yo'q.
- **Hal etilmagan qoidalar:** kutish ro'yxati, bekor qilish shartlari va mijozni nima bilan aniqlash (email yoki hisob). Har biri uchun javob beradigan shaxs ko'rsatilgan.
- **Uchta funksional ehtiyoj:** bo'sh joy (17 tadan 20 ta sotilgan, "3 ta chipta qoldi", hech narsa saqlanmaydi), bron ("Booked, reference B-018", bitta yangi tasdiqlangan bron), holatni tekshirish (faqat o'qish).
- **Bron qoidalari:** sig'im (tasdiqlangan bronlar 20 tadan oshmaydi) va bir mijozga bir konsertda bitta bron. Ikkala qoida ham ma'lumotlar bazasida ta'minlanishi kerak, faqat `if` bilan emas. Sotilgan va takroriy bron misollari berilgan.
- **Sifat talablari:** bir vaqtdagi so'rovlarda to'g'rilik (maqsad: 0 ta ortiqcha bron, taklif, o'lchanmagan), klaviatura bilan ishlaydigan mijozlar uchun qulaylik, va chiqarilish kunidagi javob tezligi (maqsad kelishiladi).
- **Kontekst eskizi:** Customer, Ticket app, Organiser, Support va Email provider, xabarlar belgilangan. Ticket app bron ma'lumotlariga egalik qiladi.
- **Beshta atama:** konsert, sig'im, tasdiqlangan bron, sotilgan, bekor qilish.
- **Jamoa mas'uliyati:** muallif ko'pgina qismlarni tayyorlagan va brifga qarab tekshirgan. Sherigining ulushi yozilmagan.
- **Vositalar tekshiruvi:** macOS'da VS Code va Python mavjud. Git o'sha paytda tekshirilmagan. Ma'lumotlar bazasi vositalari mavjud.
- **Tengdoshlar fikri:** o'z-o'zini tekshirish. Bir jumla "sig'imdan ko'p chipta sotmasligi kerak" dan aniq qoidaga o'zgartirilgan. Dalil belgisi: taklif qilingan, tasdiqlanmagan.
- **Shaxsiy mulohaza:** sig'im qoidasi, muallifning hissasi va qoida bir nechta serverda qayerda turishi kerakligi haqidagi ochiq savol.

Holat: topshirilgan. Cheklov: bir vaqtdagi qoida yozilgan, lekin haqiqiy ma'lumotlar bazasida hali sinalmagan.

### P02 · Operatsion tizimga kirish, yadrolar va jarayon hayot sikli
Laboratoriya: ota Python dasturi bola dasturni ishga tushiradi. Bola Enter kutadi, kichik fayl saqlaydi va chiqadi. Muallif uni macOS'da (Apple Silicon, Python 3.13) 2026-yil 24-oktabrda, taxminan 12:15 da bajargan.

Kuzatilgani (o'z ishlashi):
- Bola PID **15188**, ota PID **15169**. Bola platformani Darwin deb xabar bergan va 0.75 soniyada 8 460 407 ta aylanish bajargan.
- Ketma-ketlik: yaratildi (Popen) → CPU ishi → `input()` da bloklandi → Enter bosildi → fayl saqlandi → 7 kodi bilan chiqdi → otaning `wait()` qaytdi.
- O'zgartirilgan kod: `EXIT_CODE` 7 dan 3 ga. Bashorat: chiqish kodi 3 va fayl ichida `requested_exit_code=3`. Haqiqat: bola PID 15347, ota PID 15343, chiqish kodi 3, fayl bashoratdagidek yangilandi. Ota faqat 7 ni qabul qilgani uchun "unexpected child result" deb yozdi. Bu ota va bola o'rtasidagi yozilmagan shartnomani ko'rsatadi.

Kuzatilmagani (halollik bilan yozilgan):
- `ps` buyrug'i muallif xato bilan kiritgan namuna PID (12345) bilan ishga tushirilgan. Bola allaqachon chiqib ketgan edi, shuning uchun chiqishda faqat sarlavha bor edi. **Holat, oqimlar va xotira (VSZ, RSS) o'lchanmagan.** To'g'ri usul: bolani kutish holatida ushlab turib, ikkinchi terminalda `ps -p <PID>` ishlatish.

Tushuntirilgan tushunchalar:
- `fork()` ota nusxasini yaratadi. `exec` bola ichidagi dasturni almashtiradi, lekin PID ni saqlaydi. `wait` chiqish kodini oladi va zombi jarayonni olib tashlaydi.
- Windows'da `fork()` yo'q. `CreateProcess` jarayonni yaratadi va dasturni bitta chaqiruvda yuklaydi.
- Tayyor va bloklangan holat farqli: bloklangan jarayon biror hodisani (bu yerda tugma bosilishini) kutadi.
- Saqlangan fayl jarayon tugagach ham qoladi, chunki uni yadro va fayl tizimi boshqaradi. Muvaffaqiyatli `write()` quvvat uzilganda saqlanishini kafolatlamaydi; buning uchun `fsync` kerak.

Dasturlash tili qarori (vaqtinchalik): kelajakdagi o'quv loyihasi uchun C#/.NET 10. Sababi: macOS, Windows va Linuxda ishlaydi va kurs boshlang'ich loyihasida ishlatiladi. Hali tekshirilishi kerak: har bir jamoa noutbukiga o'rnatish, IDE qo'llab-quvvatlashi va PostgreSQL drayveri. Qayta ko'rib chiqiladi: agar ustoz Java talab qilsa yoki noutbukka .NET 10 o'rnatilmasa.

Holat: topshirilgan. Cheklov: faqat bir marta bajarilgan; jarayon holati va xotira maydonlari yo'q.
