def require_fields(data, fields):
    """Return an error string if any field is missing or blank, else None."""
    data = data or {}
    for f in fields:
        v = data.get(f)
        if v is None or (isinstance(v, str) and not v.strip()):
            return f"'{f}' is required"
    return None


def parse_int(value, name, minimum=0):
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None, f"'{name}' must be a whole number"
    if n < minimum:
        return None, f"'{name}' must be at least {minimum}"
    return n, None
