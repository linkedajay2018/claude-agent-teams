"""Background worker: drains the job queue and fulfills orders."""

from sample_app.queue.jobs import dequeue
from sample_app.storage.repository import OrderRepository
from sample_app.notifications.email import send_order_confirmation

_repo = OrderRepository()


def process_next_job():
    """Processes one queued job, if any. Returns the order_id handled, or None."""
    job = dequeue()
    if job is None:
        return None
    if job["job_type"] == "process_order":
        order_id = job["payload"]["order_id"]
        order = _repo.get_order(order_id)
        _repo.set_status(order_id, "fulfilled")
        send_order_confirmation(order_id, order["customer_id"])
        return order_id
    return None
