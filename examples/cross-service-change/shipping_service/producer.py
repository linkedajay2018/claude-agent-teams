"""Producer of the OrderShipped event."""

from contract.events import validate_event


def ship_order(order_id, customer_id):
    event = {"order_id": order_id, "customer_id": customer_id}
    validate_event(event)
    return event
