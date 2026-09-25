"""Consumer of OrderShipped: notifies the customer once an order ships."""

from contract.events import validate_event


def handle_order_shipped(event):
    validate_event(event)
    return f"Shipment notification sent for order {event['order_id']} to {event['customer_id']}"
