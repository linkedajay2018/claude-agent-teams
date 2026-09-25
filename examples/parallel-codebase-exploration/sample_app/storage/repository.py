"""In-memory persistence for orders and customers."""

_ORDERS = {}
_CUSTOMER_EMAILS = {
    "cust-1": "alice@example.com",
    "cust-2": "bob@example.com",
}


class OrderRepository:
    def save_order(self, order_id, customer_id, total, status="pending"):
        _ORDERS[order_id] = {
            "order_id": order_id,
            "customer_id": customer_id,
            "total": total,
            "status": status,
        }

    def get_order(self, order_id):
        return _ORDERS.get(order_id)

    def set_status(self, order_id, status):
        if order_id in _ORDERS:
            _ORDERS[order_id]["status"] = status

    def get_customer_email(self, customer_id):
        return _CUSTOMER_EMAILS.get(customer_id)
