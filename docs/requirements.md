# Requirements: hotel booking app

## R1 · Search
A guest or receptionist can list the rooms that are free for given dates.
Check: empty hotel, 12–14 November → R7, R8.
Proof: Free rooms 12-14 Nov: R7, R8

## R2 · Book
A guest or receptionist can book a free room. The app answers with a reservation id.
Check: Maya books R7 for 12–14 November → Accepted R101.
Proof: Maya books R7 12-14 Nov: Accepted R101

## R3 · No clash
A room never has two Confirmed bookings on the same night. Check-out must be after check-in.
Check: Omar asks for R7 on 13–15 → Unavailable. 15–15 → InvalidDates.
More examples:
- Maya R7 12–14 → Confirmed (nights of the 12th and 13th)
- Omar R7 13–15 → Unavailable (night of the 13th is shared)
- Nora R7 14–16 → Accepted (no shared night: Maya leaves on the 14th)
- R8 is booked 20–22 Nov. Request R8 22–24 → Accepted (check-out day 22 is free)
- R8 is booked 20–22 Nov. Request R8 21–23 → Unavailable (night of the 21st is shared)
Proof: Omar books R7 13-15 Nov: Unavailable
Proof: Omar books R8 15-15 Nov: InvalidDates

## R4 · Cancel
A booking can be cancelled. It is kept as Cancelled and no longer blocks the room.
Check: Maya cancels R101 → R7 is free again for 12–14.
Proof: Maya cancels R101: True, then Free rooms 12-14 Nov: R7, R8

## R5 · View
A booking can be looked up by its id.
Check: R101 → Maya, R7, 12–14 November, Confirmed.
Proof: store.find("R101") returns Maya's reservation (used by cancel in the demo)

## R6 · Failed message
If the confirmation cannot be sent, the booking stays saved and Accepted, and the failure is reported.
Check: the sender fails (mail server down) → Accepted R101, notification_failed = True, the store still has 1 reservation.
Proof: test_a_failed_confirmation_keeps_the_booking ... ok
