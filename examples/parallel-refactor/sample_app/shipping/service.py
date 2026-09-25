from sample_app.common.currency import format_currency


def get_shipping_quote(base_cents, surcharge_cents):
    return format_currency(base_cents + surcharge_cents)
