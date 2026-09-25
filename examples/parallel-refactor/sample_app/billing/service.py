def _format_currency(cents):
    return f"${cents / 100:.2f}"


def get_invoice_total(line_item_cents):
    return _format_currency(sum(line_item_cents))
