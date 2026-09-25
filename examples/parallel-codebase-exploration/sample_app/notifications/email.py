"""Order-related customer notifications."""

from sample_app.storage.repository import OrderRepository

_repo = OrderRepository()


def send_order_confirmation(order_id, customer_id):
    """Looks the customer's email up directly from storage rather than
    being handed it by the caller, and 'sends' the confirmation."""
    email = _repo.get_customer_email(customer_id)
    if email is None:
        return False
    print(f"[notifications] confirmation for order {order_id} sent to {email}")
    return True
