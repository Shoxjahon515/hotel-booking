# Quality scenarios

## Stakeholders

| Who | What they care about |
|---|---|
| Guest | Finds a free room quickly; never loses a booking |
| Receptionist | Never promises one room twice; can cancel at the desk |
| Hotel manager (domain expert) | Knows the rules; wants deposits and SMS soon |
| Development team | Can change one area without breaking the others |
| Email/SMS and payment providers | Outside systems that can be slow or down |

## S1 · Performance: searching free rooms stays fast

| Part | S1 |
|---|---|
| Source | 200 guests |
| Stimulus | They search free rooms for 12–14 Nov |
| Environment | All within one minute, normal load |
| Artifact | The free-room search: BookingService.find_free_rooms |
| Response | Every guest gets the correct list of free rooms |
| Measure | p95 response time ≤ 1 second |
| Checked in | P08 (cache) and P23 (load test) |

## S2 · Data integrity: no double booking

| Part | S2 |
|---|---|
| Source | 100 pairs of guests |
| Stimulus | Each pair books the same room for the same nights at the same moment |
| Environment | Normal operation, requests arriving in parallel |
| Artifact | BookingService.reserve and the reservation store |
| Response | Exactly one reservation per pair is Confirmed; the other guest gets Unavailable |
| Measure | 0 double bookings out of 100 pairs |
| Checked in | P09 (today `python main.py --race` still shows 2 Confirmed) |

## S3 · Availability: a failed message keeps the booking

| Part | S3 |
|---|---|
| Source | The email provider |
| Stimulus | It stops answering |
| Environment | For 10 minutes, during normal bookings |
| Artifact | BookingService.reserve and the notification sender |
| Response | Every valid booking is still Accepted and saved; the failed message is reported |
| Measure | 0 lost bookings; every failed message is counted |
| Checked in | P04 (R6 test, done) and P10 |

## S4 · Security: a guest sees only their own reservations

| Part | S4 |
|---|---|
| Source | A guest (Omar) |
| Stimulus | He tries 100 times to read another guest's reservation (R101, Maya's) |
| Environment | Over the public API, logged in as himself |
| Artifact | Looking up a reservation by id (View a booking) |
| Response | Every attempt is refused; Maya's data is never shown |
| Measure | 0 reservations shown to the wrong guest out of 100 attempts |
| Checked in | P21 |

## S5 · Modifiability: adding SMS confirmations

| Part | S5 |
|---|---|
| Source | The hotel manager |
| Stimulus | Asks for SMS confirmations as well as email |
| Environment | During development, between two releases |
| Artifact | The notification code and BookingService |
| Response | SMS is added as one new sender class; BookingService is not edited |
| Measure | BookingService unchanged; at most 2 files change |
| Checked in | P04 (SmsNotificationSender and its test, done) |

## S6 · Sustainability: less energy for the same searches

| Part | S6 |
|---|---|
| Source | The development team |
| Stimulus | Ships a change to the free-room search (for example a cache) |
| Environment | The same 1,000 completed searches, measured before and after the change |
| Artifact | The free-room search and the server it runs on |
| Response | The same correct answers, with less energy per completed search |
| Measure | At least 20% fewer watt-hours per 1,000 completed searches |
| Checked in | P08 and P24 |
