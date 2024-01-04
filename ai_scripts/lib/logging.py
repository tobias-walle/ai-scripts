from typing import Callable, Iterable
from rich import print
from rich.console import RenderableType
from rich.live import Live


def print_step(msg: str):
    print(f"[grey74]> {msg}[/]")


def print_status(msg: str):
    print(f"[grey54]- {msg}[/]")


def print_error(msg: str):
    print(f"[bright_red]- ERROR: {msg}[/]")


def print_stream(
    stream: Iterable[str], render: Callable[[str], RenderableType] = lambda s: s
) -> str:
    with Live() as live:
        buffer = ""
        for token in stream:
            buffer += token
            live.update(render(buffer))
        return buffer
