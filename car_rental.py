"""A small demonstration car-rental booking system.

The module uses an in-memory SQLite database and prints a short demonstration
when run directly.
"""

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

# Global rental state used by the built-in demonstration.
fleet = {}
bookings = []
conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE customers (name TEXT, licence TEXT, phone TEXT)"
)


def add_car(plate, model="Unknown", daily_rate=0, features=None):
    """Add a car to the fleet and return its record."""
    if not plate:
        raise ValueError("Registration plate cannot be empty.")
    if daily_rate < 0:
        raise ValueError("Daily rate cannot be negative.")
    if features is None:
        features = []
    fleet[plate] = {
        "model": model,
        "rate": daily_rate,
        "available": True,
        "features": features,
    }
    return fleet[plate]


def register_customer(name, licence, phone):
    """Register a customer using a parameterised SQL query."""
    conn.execute(
        "INSERT INTO customers (name, licence, phone) VALUES (?, ?, ?)",
        (name, licence, phone),
    )


def find_customer(name):
    """Return matching customer records without interpolating SQL."""
    return conn.execute(
        "SELECT * FROM customers WHERE name = ?", (name,)
    ).fetchall()


def rent_car(plate, customer, start, end):
    """Create a booking, requiring a registered customer and valid dates."""
    if not find_customer(customer):
        raise ValueError("Customer not registered.")
    if plate not in fleet:
        raise ValueError(f"Unknown registration plate: {plate}")
    if not fleet[plate]["available"]:
        raise ValueError("Car is not currently available.")

    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    days = (end_date - start_date).days
    if days <= 0:
        raise ValueError("End date must be after start date.")

    cost = days * fleet[plate]["rate"]
    fleet[plate]["available"] = False
    bookings.append(
        {
            "code": booking_code(),
            "plate": plate,
            "customer": customer,
            "days": days,
            "cost": cost,
        }
    )
    return cost


def return_car(plate, km_driven):
    """Mark a known car available and return its extra-kilometre charge."""
    if plate not in fleet:
        raise ValueError(f"Unknown registration plate: {plate}")
    if km_driven < 0:
        raise ValueError("Kilometres driven cannot be negative.")

    fleet[plate]["available"] = True
    return max(0, km_driven - 300) * 5


def booking_code():
    """
    Generate a booking code using a cryptographically strong
    token source.
    """
    return f"BK-{secrets.randbelow(90000) + 10000}"


def licence_hash(licence):
    """Hash a licence identifier for this demonstration.

    SHA-256 is used here instead of SHA-1. This is a deterministic hash,
    not encryption; real applications should consider keyed hashing or
    a privacy-preserving storage design for sensitive identifiers.
    """
    return hashlib.sha256(licence.encode("utf-8")).hexdigest()


def apply_promo(rule, amount):
    """Apply only supported promotion rules; do not execute arbitrary code."""
    if not isinstance(amount, (int, float)) or isinstance(amount, bool):
        raise ValueError("Amount must be numeric.")
    if amount < 0:
        raise ValueError("Amount cannot be negative.")

    supported_rules = {
        "10_percent_off": lambda value: value * 0.9,
        "20_percent_off": lambda value: value * 0.8,
    }
    try:
        calculation = supported_rules[rule]
    except KeyError as exc:
        raise ValueError("Unsupported promotion rule.") from exc
    return calculation(amount)


def is_valid_plate(plate):
    """Return True if plate matches the expected Indian registration shape."""
    return bool(re.fullmatch(r"[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}", plate))


def write_receipt(booking):
    """
    Write a receipt to a safely created temporary file and return
    its path.
    """
    receipt_text = (
        f"Booking {booking['code']}: {booking['plate']} for "
        f"{booking['days']} days = Rs.{booking['cost']:.2f}\n"
    )
    file_descriptor, path = tempfile.mkstemp(
        suffix=".txt", prefix="car_rental_receipt_"
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as receipt_file:
            receipt_file.write(receipt_text)
    except Exception:
        Path(path).unlink(missing_ok=True)
        raise
    return path


def admin_login(user, password):
    """Check credentials configured outside the source code.

    Set CAR_RENTAL_ADMIN_USER and CAR_RENTAL_ADMIN_PASSWORD in the process
    environment. Production systems should use managed credentials and
    protected password hashes rather than plain environment values.
    """
    expected_user = os.environ.get("CAR_RENTAL_ADMIN_USER")
    expected_password = os.environ.get("CAR_RENTAL_ADMIN_PASSWORD")
    if not expected_user or not expected_password:
        return False
    return hmac.compare_digest(user, expected_user) and hmac.compare_digest(
        password, expected_password
    )


def available_cars():
    """Return registration plates for cars that are currently available."""
    return [
        plate
        for plate, car in fleet.items()
        if car["available"]
    ]


def main():
    """Run a short demonstration of the car-rental functions."""
    add_car("KA01AB1234", "Swift", 1500)
    add_car("KA02CD5678", "Innova", 3000)
    try:
        add_car("KA03EF9999", "Nexon", -500)
    except ValueError as error:
        print("Rejected invalid car:", error)

    register_customer("Ravi", "DL-0420110012345", "9845012345")
    register_customer("Meera", "DL-0420110099999", "9845099999")

    print(
        "Rent Swift:",
        rent_car("KA01AB1234", "Ravi", "2026-11-01", "2026-11-04"),
    )
    try:
        rent_car("KA01AB1234", "Ravi", "2026-11-02", "2026-11-03")
    except ValueError as error:
        print("Rejected overlapping rental:", error)

    try:
        rent_car("KA02CD5678", "Ravi", "2026-11-10", "2026-11-07")
    except ValueError as error:
        print("Rejected invalid rental dates:", error)

    print("Lookup injection attempt:", find_customer("x' OR '1'='1"))
    print("Extra km charge:", return_car("KA01AB1234", 420))
    try:
        return_car("XX00XX0000", 50)
    except ValueError as error:
        print("Rejected unknown car return:", error)

    print("Promo price:", apply_promo("10_percent_off", 4500))
    print("Plate valid?", is_valid_plate("KA01AB1234"))
    print("Licence hash:", licence_hash("DL-0420110012345"))
    demo_user = os.environ.get("CAR_RENTAL_ADMIN_USER", "")
    demo_password = os.environ.get("CAR_RENTAL_ADMIN_PASSWORD", "")
    print("Admin:", admin_login(demo_user, demo_password))
    print("Available:", available_cars())
    print("Receipt saved to:", write_receipt(bookings[0]))


if __name__ == "__main__":
    main()
