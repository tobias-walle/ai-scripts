from rich import print


def print_step(msg: str):
    print(f"[grey74]> {msg}[/]")


def print_status(msg: str):
    print(f"[grey54]- {msg}[/]")


def print_error(msg: str):
    print(f"[bright_red]- ERROR: {msg}[/]")
