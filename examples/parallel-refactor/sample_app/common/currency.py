def format_currency(cents):
    """The shared implementation every module should import instead of duplicating."""
    return f"${cents / 100:.2f}"
