from typing import Callable, Iterable
from rich import print
from rich.console import RenderableType
from rich.live import Live

COLOR_GRAY_1 = "grey74"
COLOR_GRAY_2 = "grey54"
COLOR_RED = "bright_red"


def print_step(msg: str):
    print(f"[{COLOR_GRAY_1}]> {msg}[/]")


def print_status(msg: str):
    print(f"[{COLOR_GRAY_2}]- {msg}[/]")


def print_error(msg: str):
    print(f"[{COLOR_RED}]- ERROR: {msg}[/]")


def print_stream(
    stream: Iterable[str],
    render: Callable[[str], RenderableType] = lambda s: s,
    prefix="",
) -> str:
    with Live(vertical_overflow="visible") as live:
        buffer = prefix
        for token in stream:
            buffer += token
            # First rerender the output on every update
            live.update(render(buffer))
        live.update("")
    # Then render buffer normally, so text wrapping works like you would expect
    print(render(buffer))
    return buffer
