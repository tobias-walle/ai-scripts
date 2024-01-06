import sys
from typing import Callable, Iterable
from rich import print
from rich.console import RenderableType
from rich.live import Live
from rich.markdown import Markdown
from rich.syntax import Syntax

COLOR_GRAY_1 = "grey74"
COLOR_GRAY_2 = "grey54"
COLOR_RED = "bright_red"

CODE_THEME = "dracula"


def print_step(msg: str):
    print(f"[{COLOR_GRAY_1}]> {msg}[/]", file=sys.stderr)


def print_status(msg: str):
    print(f"[{COLOR_GRAY_2}]- {msg}[/]", file=sys.stderr)


def print_error(msg: str):
    print(f"[{COLOR_RED}]- ERROR: {msg}[/]", file=sys.stderr)


def render_syntax(text: str, language: str) -> Syntax:
    return Syntax(text, language, theme=CODE_THEME, background_color="default")


def render_markdown(text: str) -> Markdown:
    return Markdown(text, code_theme=CODE_THEME, inline_code_theme=CODE_THEME)


def print_stream(
    stream: Iterable[str],
    render: Callable[[str], RenderableType] = lambda s: s,
    prefix="",
) -> str:
    with Live() as live:
        buffer = prefix
        for token in stream:
            buffer += token
            # First render the output on every update
            live.update(render(limit_lines(buffer, live.console.height)))
        live.update("")
        buffer = buffer.strip()
        # Then render buffer normally, so text wrapping works like you would expect
        live.console.print(render(buffer))
    return buffer


def limit_lines(text: str, n_lines: int) -> str:
    lines = text.splitlines()
    return "\n".join(lines[-n_lines:])
