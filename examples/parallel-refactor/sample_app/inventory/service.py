from sample_app.common.currency import format_currency


def get_restock_cost(unit_cost_cents, quantity):
    return format_currency(unit_cost_cents * quantity)
