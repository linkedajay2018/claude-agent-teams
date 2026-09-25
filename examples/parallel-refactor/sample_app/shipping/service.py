def _format_currency(cents):
    return f"${cents / 100:.2f}"


def get_shipping_quote(base_cents, surcharge_cents):
    return _format_currency(base_cents + surcharge_cents)
