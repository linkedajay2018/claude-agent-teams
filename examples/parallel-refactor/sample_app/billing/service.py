from sample_app.common.currency import format_currency


def get_invoice_total(line_item_cents):
    return format_currency(sum(line_item_cents))
