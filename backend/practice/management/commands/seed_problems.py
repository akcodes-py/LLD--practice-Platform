"""Seed the 5 MVP LLD problems (idempotent: update-or-create by slug)."""
from django.core.management.base import BaseCommand

from practice.models import Problem

PROBLEMS = [
    {
        "slug": "parking-lot",
        "title": "Parking Lot",
        "summary": "Design a multi-floor parking system with flexible spot allocation, ticketing, and payments.",
        "difficulty": "beginner",
        "tags": ["allocation", "ticketing", "payments", "concurrency"],
        "estimated_minutes": 45,
        "description": (
            "A shopping-mall operator needs a parking-lot system for a building with multiple floors. "
            "Vehicles of different sizes arrive concurrently, take a ticket at entry, park in a suitable spot, "
            "and pay on exit based on time parked and vehicle type. The operator wants to add new vehicle types, "
            "pricing rules, and payment methods without rewriting the core."
        ),
        "functional_requirements": [
            "Support multiple floors, each with spots sized for motorcycle, car, and bus.",
            "Assign the nearest suitable free spot on entry and issue a ticket (ticket id, entry time, spot).",
            "Release the spot on exit and compute the fee from duration and vehicle type.",
            "Accept multiple payment methods (cash, card, UPI) and record payment status.",
            "Show real-time availability per floor and vehicle type.",
            "Handle two entries allocating concurrently without double-booking a spot.",
        ],
        "constraints": [
            "One vehicle occupies exactly one spot sized for it or larger.",
            "Ticket ids must be unique; a lost ticket must still allow exit with verification.",
            "Fee computation must be explainable from entry/exit timestamps.",
        ],
        "design_considerations": [
            "Where does allocation logic live so a new spot-assignment strategy can be plugged in?",
            "How do Vehicle, Spot, Ticket, and Payment depend on each other (and on abstractions)?",
            "Which parts vary independently: pricing, payment method, spot search?",
            "What interfaces would let you add EV charging spots later?",
        ],
        "edge_cases": [
            "Lot full for a vehicle type while other sizes have space.",
            "Two attendants allocate the last spot at the same time.",
            "Lost ticket, unreadable plate, or clock skew between entry and exit.",
            "Payment fails after the barrier is told to open.",
        ],
    },
    {
        "slug": "elevator-system",
        "title": "Elevator System",
        "summary": "Design multi-elevator dispatch with direction-aware scheduling and failure handling.",
        "difficulty": "advanced",
        "tags": ["scheduling", "state machine", "concurrency"],
        "estimated_minutes": 60,
        "description": (
            "An office tower with 20 floors and 4 elevators needs a control system. Passengers press hall buttons "
            "(up/down) and cabin buttons (floor). The system dispatches the best elevator, moves cabins efficiently, "
            "opens/closes doors safely, and keeps working when one elevator is under maintenance."
        ),
        "functional_requirements": [
            "Serve hall calls (floor + direction) and cabin calls (destination floor).",
            "Dispatch one elevator per hall call using a stated strategy (e.g. nearest, SCAN/LOOK).",
            "Model cabin states: idle, moving, doors open/closed, maintenance.",
            "Prevent unsafe moves: never move with doors open; respect capacity limits.",
            "Isolate a faulty elevator without stopping the whole system.",
            "Report cabin position and direction for display panels.",
        ],
        "constraints": [
            "A hall call is served exactly once even with concurrent requests.",
            "Doors must fully close before motion; obstruction reopens doors.",
            "Scheduling decision must be explainable (why this elevator?).",
        ],
        "design_considerations": [
            "Who owns scheduling: a dispatcher, the elevators, or both (and why)?",
            "How to represent requests so the strategy can be swapped (Strategy pattern)?",
            "What state machine governs a cabin, and where do door/timeout rules live?",
            "How do observers (displays, buttons) stay consistent without tight coupling?",
        ],
        "edge_cases": [
            "All elevators at capacity during morning rush.",
            "Power flicker mid-transit; recovery to a safe floor.",
            "Hall button pressed repeatedly; duplicate requests.",
            "An elevator stuck with doors open; timeout and alert flow.",
        ],
    },
    {
        "slug": "vending-machine",
        "title": "Vending Machine",
        "summary": "Design product inventory, coin handling, and a safe dispense workflow.",
        "difficulty": "beginner",
        "tags": ["state machine", "inventory", "payments"],
        "estimated_minutes": 30,
        "description": (
            "A vending-machine vendor wants software for machines selling snacks and drinks. Users insert coins/notes, "
            "select a product, receive the item and change. Operators restock items and collect cash. "
            "The machine must never dispense without payment nor take payment without the option to refund."
        ),
        "functional_requirements": [
            "Track products (code, name, price, quantity) per slot.",
            "Accept denominations, show inserted balance, and return change.",
            "Dispense only when balance covers price and stock exists.",
            "Refund on cancel at any point before dispense.",
            "Support restock and price updates by an operator.",
            "Record each sale for later reconciliation.",
        ],
        "constraints": [
            "No negative inventory; concurrent selections cannot oversell the last item.",
            "Change can only use available denominations; otherwise offer cancel.",
            "Every money movement is logged (inserted, refunded, collected).",
        ],
        "design_considerations": [
            "What states does a transaction move through (idle, accepting, selected, dispensing)?",
            "Where do pricing and change-making rules live so denominations can change?",
            "How are cash, inventory, and dispense coordinated atomically?",
            "What interface would let a card reader be added later?",
        ],
        "edge_cases": [
            "Exact-change-only situation; insufficient coins for change.",
            "Item jammed after payment; refund vs retry policy.",
            "Power loss mid-dispense.",
            "Invalid product code or empty slot selected.",
        ],
    },
    {
        "slug": "library-management-system",
        "title": "Library Management System",
        "summary": "Design catalog search, lending with due dates, fines, and reservations.",
        "difficulty": "intermediate",
        "tags": ["catalog", "lending", "fines", "search"],
        "estimated_minutes": 45,
        "description": (
            "A city library needs a system for members to search the catalog, borrow books, return them, "
            "pay late fines, and reserve books that are checked out. Librarians add/remove copies and manage members. "
            "The catalog must stay searchable as the collection grows."
        ),
        "functional_requirements": [
            "Search books by title, author, ISBN, and subject.",
            "Borrow: check availability, create a loan with due date, enforce per-member loan limits.",
            "Return: close the loan, compute fines for overdue days, free the copy.",
            "Reserve checked-out books; notify the next member on return.",
            "Register members and track loan history and outstanding fines.",
            "Librarians can add/remove book copies and update catalog entries.",
        ],
        "constraints": [
            "A physical copy can be on loan to at most one member at a time.",
            "Fines must be reproducible from due date, return date, and rate.",
            "Reservations are served FIFO per book.",
        ],
        "design_considerations": [
            "Book (title-level) vs BookCopy (physical item): why separate them?",
            "Where do loan rules (limits, durations, fines) live so policy changes are local?",
            "How do search indexes stay decoupled from lending workflows?",
            "What notifies reservation holders without tangling lending code (Observer/events)?",
        ],
        "edge_cases": [
            "Two members reserve the last copy simultaneously.",
            "Member with unpaid fines tries to borrow.",
            "Book lost or damaged on return.",
            "Duplicate ISBN entries from bad imports.",
        ],
    },
    {
        "slug": "food-ordering-system",
        "title": "Food Ordering System",
        "summary": "Design restaurant menus, order tracking, payments, and delivery assignment.",
        "difficulty": "intermediate",
        "tags": ["ordering", "payments", "tracking", "notifications"],
        "estimated_minutes": 50,
        "description": (
            "A food-delivery startup needs an ordering system: customers browse restaurants and menus, place orders, "
            "pay online, and track preparation and delivery. Restaurants accept/reject orders and update preparation "
            "status. Delivery partners are assigned and tracked."
        ),
        "functional_requirements": [
            "Browse restaurants and menus; search by cuisine and dish.",
            "Place an order (items, quantities, address) and compute the total with taxes and fees.",
            "Pay online; only confirmed payments enter the kitchen queue.",
            "Track order states: placed, confirmed, preparing, ready, picked up, delivered, cancelled.",
            "Restaurants manage menus, availability, and preparation times.",
            "Assign a delivery partner and notify the customer on each state change.",
        ],
        "constraints": [
            "An order cannot move backward in state; cancel is only allowed before preparation starts.",
            "Totals must be recomputable from items, taxes, and fees.",
            "One order has exactly one active delivery assignment at a time.",
        ],
        "design_considerations": [
            "What owns the order state machine, and how are invalid transitions rejected?",
            "How do pricing (items, taxes, fees, discounts) compose without tangling?",
            "How do restaurant, payment, and delivery modules stay decoupled (events/interfaces)?",
            "Where would a promo-code or surge-fee rule plug in later?",
        ],
        "edge_cases": [
            "Payment succeeds but the restaurant rejects the order; refund flow.",
            "Item goes out of stock after checkout starts.",
            "Delivery partner cancels mid-delivery; reassignment.",
            "Duplicate order submission from double-click or retry.",
        ],
    },
]


class Command(BaseCommand):
    help = "Seed the MVP LLD problems."

    def handle(self, *args, **options):
        for item in PROBLEMS:
            Problem.objects.update_or_create(slug=item["slug"], defaults=item)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(PROBLEMS)} problems."))
