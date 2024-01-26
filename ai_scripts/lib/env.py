import os


def is_debbuging() -> bool:
    return os.getenv("DEBUG") == "1"
