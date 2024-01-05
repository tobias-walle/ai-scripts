#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import sys
import subprocess
from typing import Dict, List, Optional, TypeVar
from openai.types.chat import ChatCompletionMessageParam
from rich.console import Console
import re
import mdformat

from ai_scripts.lib.logging import (
    COLOR_GRAY_1,
    print,
    print_step,
    print_stream,
    render_markdown,
)
from ai_scripts.lib.model import OpenAIGPT4TurboModel


def main():
    parser = argparse.ArgumentParser(
        prog="ai-chat",
        description="Chat with the ai in an markdown file",
    )
    parser.add_argument(
        "file",
        help="The file to chat in",
    )
    args = parser.parse_args()
    file = Path(args.file)

    console = Console()
    model = OpenAIGPT4TurboModel()
    editor = os.getenv("EDITOR", "vi")

    if not file.exists():
        file.write_text(
            f"{format_role('system')}\nYou are a helpful assistant.\n\n{format_role('user')}\n"
        )

    while True:
        md = file.read_text()
        chat = parse_chat(md)
        last_msg = last_item(chat)
        if last_msg is not None and last_msg["role"] == "user":
            console.clear()
            header = f"{format_role('assistant')}\n"
            answer = print_stream(model.stream(chat), render_markdown, prefix=header)
            md += f"\n\n{answer}"
            md = md.strip() + f"\n\n{format_role('user')}\n\n"
            file.write_text(mdformat.text(md, options={"wrap": 80}))
            cancel = (
                console.input(f"\n\n[{COLOR_GRAY_1}]Continue? [Y,n]: [/]").lower()
                == "n"
            )
            if cancel:
                break
        else:
            result = subprocess.call([editor, file])
            if result != 0:
                print(f"Failed to open the editor. Error code: {result}")
                sys.exit(1)

            md = file.read_text()
            last_msg = last_item(parse_chat(md))
            if last_msg is None or last_msg["role"] != "user":
                print_step("Last message is not of role 'user'. Exiting...")
                break


def parse_chat(md: str) -> List[ChatCompletionMessageParam]:
    messages: List[Dict[str, str]] = []
    message: Optional[Dict[str, str]] = None
    for line in md.strip().splitlines():
        role = parse_role(line)
        if role is not None:
            if message is not None:
                message["content"] = message["content"].strip()
                messages.append(message)
            message = {"role": role, "content": ""}  # type: ignore
        else:
            if message is not None:
                message["content"] += f"{line}\n"
    if message is not None:
        messages.append(message)

    messages = [m for m in messages if m["content"] != ""]
    return messages  # type: ignore


def format_role(role: str) -> str:
    return f"# --- {role} ---"


role_regex = re.compile(r"# --- (.+) --- *$")


def parse_role(line: str) -> Optional[str]:
    role_match = role_regex.match(line)
    if role_match:
        return role_match.group(1)
    else:
        return None


T = TypeVar("T")


def last_item(list: List[T]) -> Optional[T]:
    return None if len(list) == 0 else list[-1]


if __name__ == "__main__":
    main()
