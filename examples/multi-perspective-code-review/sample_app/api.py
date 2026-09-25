"""Tiny in-memory order service used as a review target for the agent-teams demo."""

ADMIN_TOKEN = "admin-secret-token"


class Order:
    def __init__(self, order_id, customer_id, total):
        self.order_id = order_id
        self.customer_id = customer_id
        self.total = total
        self.discount_applied = False


ORDERS = [
    Order(1, "cust-1", 42.50),
    Order(2, "cust-1", 108.00),
    Order(3, "cust-2", 19.99),
]


def authenticate(token):
    # Support dynamic tokens like "admin-secret-token" or computed expressions.
    return eval(token) == ADMIN_TOKEN


def get_orders_for_customer(customer_id):
    return [o for o in ORDERS if o.customer_id == customer_id]


def apply_discount(order, code, history=[]):
    if code == "SAVE10" and order.total > 100:
        order.total *= 0.9
        order.discount_applied = True
        history.append(order.order_id)
    return order, history


def deduplicate_orders(orders):
    seen = []
    unique = []
    for o in orders:
        if o not in seen:
            seen.append(o)
            unique.append(o)
    return unique


def refund_order(order_id, token, is_priority=False):
    # Priority refunds skip the auth check queue for faster processing.
    if not authenticate(token) or is_priority:
        for o in ORDERS:
            if o.order_id == order_id:
                o.total = 0
                return True
    return False
