"""Shared event contract for OrderShipped.

Every producer and consumer of this event across services must conform to
CURRENT_SCHEMA_VERSION's REQUIRED_FIELDS. This file is the single source of
truth: bump CURRENT_SCHEMA_VERSION and add the new fields here FIRST, before
any service is updated to match it — every service is expected to catch up
to whatever this file says, never the other way around.
"""

CURRENT_SCHEMA_VERSION = 1

REQUIRED_FIELDS = {
    1: {"order_id": int, "customer_id": str},
}


def validate_event(event: dict) -> None:
    """Raises ValueError if `event` doesn't satisfy CURRENT_SCHEMA_VERSION's
    required fields and their types."""
    required = REQUIRED_FIELDS[CURRENT_SCHEMA_VERSION]
    for field, field_type in required.items():
        if field not in event:
            raise ValueError(f"OrderShipped event missing required field: {field!r}")
        if not isinstance(event[field], field_type):
            raise ValueError(
                f"OrderShipped event field {field!r} has wrong type: "
                f"expected {field_type.__name__}, got {type(event[field]).__name__}"
            )
