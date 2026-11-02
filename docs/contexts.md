# Hotel contexts

## Words

| Word | Meaning here | Name in our code |
|---|---|---|
| Stay | Check-in to check-out, half-open: 12–14 Nov = the nights of the 12th and 13th | DateRange (check_in, check_out) |
| Reservation | Guest + room + stay + status, with an id such as R101 | Reservation (id, guest, room, stay, status) |
| Confirmed | The room is promised to this guest for these nights | ReservationStatus.CONFIRMED |
| Guest | The person a reservation is for, with a name and an email address (Maya, maya@example.com) | Guest |
| Room | A room the hotel sells, known by its number and type (R7 Standard, R8 Deluxe) | Room (number, type) |
| Room type | The kind of room: Standard or Deluxe; it decides the nightly price | Room.type |
| Nightly price | What one night in a room of this type costs; Deluxe costs more than Standard | not in code yet |
| Out of service | The room is not offered to guests, for example R8 during repairs | not in code yet |
| Cancelled | The promise is withdrawn; the nights are free again, but the reservation is kept | ReservationStatus.CANCELLED |
| Book | Ask for a room for a stay; the answer is Accepted with an id, Unavailable or InvalidDates | BookingService.reserve(guest, room, stay) |
| Cancel | Withdraw a reservation by its id, for example a guest who phones the desk | BookingService.cancel(reservation_id) |
| Free rooms | The rooms with no Confirmed reservation sharing a night with the stay | BookingService.find_free_rooms(stay) |
| Deposit | 30% of the stay's price, taken when the guest books | not in code yet |
| Paid | The deposit was taken successfully | not in code yet |
| Declined | The deposit could not be taken (for example the card was refused) | not in code yet |
| Confirmation message | The email or SMS that tells the guest "R101 is confirmed: room R7, 12–14 Nov" | NotificationSender.send_confirmation(reservation) |
| Sent | The message reached the email or SMS provider | not in code yet |
| Failed | The message could not be sent; it is recorded and reported, the booking stays | not in code yet (today only BookingResult.notification_failed) |

## Rooms

Job: knows which rooms the hotel sells.

| Word | Meaning here |
|---|---|
| Room | A room the hotel sells, known by its number and type (R7 Standard, R8 Deluxe) |
| Room type | Standard or Deluxe; it decides the nightly price |
| Nightly price | What one night in a room of this type costs |
| Out of service | The room is not offered to guests, for example R8 during repairs |

Rules this context owns:
- A room that is out of service is not offered to guests.
- The nightly price depends on the room type (Deluxe costs more than Standard).

Needs from other contexts: nothing.
Tells other contexts: nothing; it only answers "which rooms exist?" (asked by Reservations).

## Reservations

Job: decides whether a guest gets a room for some nights, and keeps every reservation.

| Word | Meaning here |
|---|---|
| Stay | Check-in to check-out, half-open: 12–14 Nov = the nights of the 12th and 13th |
| Reservation | Guest + room number + stay + status, with an id such as R101 |
| Confirmed | The room is promised to this guest for these nights |
| Cancelled | The promise is withdrawn; the nights are free again |
| Guest | The person the reservation is for: name and email address |
| Book | Ask for a room for a stay; Accepted with an id, Unavailable or InvalidDates |
| Cancel | Withdraw a reservation by its id |
| Free rooms | The rooms with no Confirmed reservation sharing a night with the stay |

Rules this context owns:
- A room never has two Confirmed reservations that share a night.
- Check-out must be after check-in.
- Cancelling a reservation frees its nights for new bookings.

Needs from other contexts: the list of rooms (Rooms); from P17, a deposit (Payments).
Tells other contexts: ReservationConfirmed (Notifications).

## Payments

Job: takes deposits and records whether they were paid.

| Word | Meaning here |
|---|---|
| Deposit | 30% of the stay's price, taken when the guest books |
| Paid | The deposit was taken successfully |
| Declined | The deposit could not be taken |

Rules this context owns:
- The deposit is 30% of the stay's price.
- Only a Paid deposit can be refunded.

Needs from other contexts: the nightly price (Rooms), to work out 30% of the stay.
Tells other contexts: nothing; it only answers Paid or Declined when Reservations asks (from P17).

## Notifications

Job: tells guests what happened, by email or SMS.

| Word | Meaning here |
|---|---|
| Confirmation message | The email or SMS that tells the guest their reservation is confirmed |
| Sent | The message reached the provider |
| Failed | The message could not be sent; it is recorded and reported |

Rules this context owns:
- A failed message is recorded as Failed and never changes the reservation (rule R6).

Needs from other contexts: nothing; the ReservationConfirmed event carries every field it needs.
Tells other contexts: nothing.

## Same word, different meaning

| Word | Rooms | Reservations | Payments | Notifications |
|---|---|---|---|---|
| Room | R8: Deluxe, nightly price, in or out of service | Only the number R8 on a reservation | Not used | Text in the message: "Room R8" |
| Status | In service / out of service | Confirmed / Cancelled | Paid / Declined | Sent / Failed |
| Cancel | Take a room off sale | Withdraw a reservation; its nights are free again | Refund a deposit | Not used |

If Notifications could change a reservation's status to Failed, one failed SMS would overwrite
Maya's Confirmed R101, R7 would look free again and Maya would lose her room because of a
message — exactly what rule R6 forbids.

## Rule owners

| Card | Rule | Owner | Why this owner |
|---|---|---|---|
| 1 | A room never has two Confirmed reservations that share a night. | Reservations | It keeps every reservation of the room, so it can check them all together. |
| 2 | Check-out must be after check-in. | Reservations | The stay is its word, and it refuses wrong dates before anything else happens. |
| 3 | Cancelling a reservation frees its nights for new bookings. | Reservations | Only Confirmed reservations block a room, and it keeps each reservation's status. |
| 4 | A room that is out of service is not offered to guests. | Rooms | It knows which rooms are on sale and which are out of service. |
| 5 | The nightly price depends on the room type. | Rooms | It keeps each room's type and price. |
| 6 | The deposit is 30% of the stay's price. | Payments | Money rules belong to Payments; it asks Rooms for the nightly price. |
| 7 | Only a Paid deposit can be refunded. | Payments | It keeps each deposit's status, Paid or Declined. |
| 8 | A failed message is recorded as Failed and never changes the reservation. | Notifications | It keeps each message's status; the reservation's status is not its data (R6). |

## Between contexts

### Reservations → Rooms: which rooms exist? (question)

Sent when: a guest searches free rooms or books a room.

What Reservations sends: nothing but the question.

The answer and its fields:
- each room's number: R7, R8
- each room's type: Standard, Deluxe

Never crosses: reservations. Rooms never learns who booked which room.

### Reservations → Payments: take a deposit (question, from P17)

Sent when: a booking holds a room and needs the deposit before it is confirmed (the P17 saga).

What Reservations sends:
- reservationId: R101
- amount: 30% of the stay's price

The answer and its fields: Paid or Declined.

Never crosses: the guest list and the booking rule. Payments never decides whether R7 is free;
a Paid deposit does not book a room.

### Reservations → Notifications: ReservationConfirmed (event)

Sent when: a reservation is saved as Confirmed.

Fields:
- reservationId: R101
- guestEmail: maya@example.com
- roomNumber: R7
- checkIn: 2026-11-12
- checkOut: 2026-11-14

Reservations does not wait for an answer. A failed message never changes R101 (rule R6).

Never crosses: Reservations' list of reservations. Notifications never reads it.
