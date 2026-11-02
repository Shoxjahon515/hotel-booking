"""Hotel booking app after P06: a modular monolith with four modules.

Each module has a public contract (its __init__.py) and internal code (internal.py):
- hotel_booking.rooms          which rooms the hotel sells
- hotel_booking.reservations   who has which room for which nights; owns the booking rule
- hotel_booking.payments       deposits and whether they were paid
- hotel_booking.notifications  telling guests what happened

Import from the module packages, for example: from hotel_booking.rooms import Room.
Only main.py and the tests may import a module's internal code.
"""
