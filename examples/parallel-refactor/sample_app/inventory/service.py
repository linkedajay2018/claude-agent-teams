def _format_currency(cents):
    return f"${cents / 100:.2f}"


def get_restock_cost(unit_cost_cents, quantity):
    return _format_currency(unit_cost_cents * quantity)
