"""Behavior check: run before and after the refactor to prove it's behavior-preserving."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sample_app.billing.service import get_invoice_total
from sample_app.shipping.service import get_shipping_quote
from sample_app.inventory.service import get_restock_cost


def main():
    assert get_invoice_total([1050, 250]) == "$13.00"
    assert get_shipping_quote(500, 150) == "$6.50"
    assert get_restock_cost(200, 12) == "$24.00"
    print("All checks passed.")


if __name__ == "__main__":
    main()
