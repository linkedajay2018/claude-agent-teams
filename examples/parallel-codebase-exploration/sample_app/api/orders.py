"""HTTP-facing order endpoints. Owns request validation, not fulfillment."""

from sample_app.storage.repository import OrderRepository
from sample_app.queue.jobs import enqueue

_repo = OrderRepository()
_next_id = [1]


def create_order(customer_id, total):
    """Accepts a new order, persists it as pending, and queues it for processing."""
    order_id = _next_id[0]
    _next_id[0] += 1
    _repo.save_order(order_id, customer_id, total)
    enqueue("process_order", {"order_id": order_id})
    return {"order_id": order_id, "status": "pending"}


def get_order_status(order_id):
    order = _repo.get_order(order_id)
    if order is None:
        return {"error": "not found"}
    return {"order_id": order_id, "status": order["status"]}
