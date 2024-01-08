def remove_none_values(d: dict) -> dict:
    """Removes None values from the given dictionary"""
    return {k: v for k, v in d.items() if v is not None}
