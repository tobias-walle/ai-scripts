import sys
from typing import Callable, Iterable
from rich import print
from rich.console import RenderableType
from rich.live import Live
from rich.markdown import Markdown
from rich.syntax import Syntax

from ai_scripts.lib.string import extract_first_code_snippet_from_markdown

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


def render_syntax(text: str, language: str) -> RenderableType:
    return Syntax(text, language, theme=CODE_THEME, background_color="default")


def render_markdown(text: str) -> RenderableType:
    return Markdown(text, code_theme=CODE_THEME, inline_code_theme=CODE_THEME)


def print_stream(
    stream: Iterable[str],
    render: Callable[[str], RenderableType] = lambda s: s,
    postprocess: Callable[[str], str] = lambda s: s,
    cancel: Callable[[str], bool] = lambda _: False,
    prefix="",
) -> str:
    with Live() as live:
        buffer = prefix
        for token in stream:
            buffer += token
            rendered_buffer = postprocess(buffer.lstrip())
            rendered_buffer = limit_lines(rendered_buffer, live.console.height)
            # First render the output on every update
            live.update(render(rendered_buffer))
            if cancel(buffer):
                break
        live.update("")
        buffer = postprocess(buffer.strip())
        # Then render buffer normally, so text wrapping works like you would expect
        live.console.print(render(buffer))
    return buffer


def print_stream_and_extract_code(stream: Iterable[str], expected_language: str) -> str:
    global language
    language = expected_language

    def postprocess(s: str):
        global language
        md = extract_first_code_snippet_from_markdown(s)
        language = md.language or expected_language
        return md.code

    def cancel(s: str):
        md = extract_first_code_snippet_from_markdown(s)
        return md.completed

    def render(s: str):
        return render_syntax(s, language)

    return print_stream(stream, render=render, postprocess=postprocess, cancel=cancel)


def limit_lines(text: str, n_lines: int) -> str:
    lines = text.splitlines()
    return "\n".join(lines[-n_lines:])
