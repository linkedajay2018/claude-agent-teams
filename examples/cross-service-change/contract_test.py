"""Contract test: proves the producer and every consumer agree on the
current OrderShipped schema version. Run before and after a coordinated
change to prove it's actually in sync across services, not just claimed to
be. This file's sample call args are owned by the contract-owner role (the
one place a generic caller of the contract is exercised); everything else
here is generic across schema versions.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contract.events import CURRENT_SCHEMA_VERSION, REQUIRED_FIELDS
from shipping_service.producer import ship_order
from billing_service.consumer import handle_order_shipped as billing_handle
from notifications_service.consumer import handle_order_shipped as notifications_handle


def main():
    event = ship_order(order_id=42, customer_id="cust-1")

    required = REQUIRED_FIELDS[CURRENT_SCHEMA_VERSION]
    for field in required:
        assert field in event, f"producer did not emit required field: {field!r}"

    billing_result = billing_handle(event)
    notifications_result = notifications_handle(event)

    for field in required:
        assert str(event[field]) in billing_result, (
            f"billing_service doesn't appear to use required field {field!r} "
            f"(got: {billing_result!r})"
        )
        assert str(event[field]) in notifications_result, (
            f"notifications_service doesn't appear to use required field {field!r} "
            f"(got: {notifications_result!r})"
        )

    print(f"Contract v{CURRENT_SCHEMA_VERSION} satisfied by producer and all consumers.")
    print(f"  event:         {event}")
    print(f"  billing:       {billing_result}")
    print(f"  notifications: {notifications_result}")


if __name__ == "__main__":
    main()
