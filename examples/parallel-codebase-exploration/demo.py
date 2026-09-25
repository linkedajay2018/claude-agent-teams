"""Runs one order through the full pipeline: api -> queue -> worker -> storage/notifications."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sample_app.api.orders import create_order, get_order_status
from sample_app.worker.processor import process_next_job


def main():
    created = create_order("cust-1", 108.00)
    assert get_order_status(created["order_id"])["status"] == "pending"

    handled = process_next_job()
    assert handled == created["order_id"]
    assert get_order_status(created["order_id"])["status"] == "fulfilled"

    print("Order pipeline ran end to end.")


if __name__ == "__main__":
    main()
