"""Consumer of OrderShipped: finalizes the invoice once an order ships."""

from contract.events import validate_event


def handle_order_shipped(event):
    validate_event(event)
    return f"Invoice finalized for order {event['order_id']} (customer {event['customer_id']})"
