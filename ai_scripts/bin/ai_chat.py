#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import sys
import subprocess
from typing import Dict, List, NotRequired, Optional, TypeVar, TypedDict
from openai.types.chat import ChatCompletionMessageParam
from rich.console import Console
import re
import tempfile
import yaml
from ai_scripts.lib.dict import remove_none_values

from ai_scripts.lib.logging import (
    COLOR_GRAY_1,
    print_error,
    print_step,
    print_stream,
    render_markdown,
)
from ai_scripts.lib.model import Models
from ai_scripts.lib.string import format_markdown


def main():
    parser = argparse.ArgumentParser(
        prog="ai-chat",
        description="Chat with the ai in an markdown file",
    )
    parser.add_argument(
        "file",
        help="The file to chat in",
        nargs="?",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        help="Pass a prompt that will be answered directly",
    )
    parser.add_argument(
        "-s",
        "--system",
        help="Pass a sytem prompt directly (Only works if the file is empty or doesn't exists yet)",
    )
    args = parser.parse_args()
    user_prompt: str = args.prompt or ""
    system_prompt: str = args.system or ""
    file_path: str = args.file or ""

    if file_path == "":
        file_path = tempfile.NamedTemporaryFile(
            prefix="chat_", suffix=".md", delete=False
        ).name
        print_step(f"Created temporay file {file_path}")
    file = Path(file_path)

    console = Console()
    editor = os.getenv("EDITOR", "vi")

    if not file.exists() or file.read_text().strip() == "":
        md = f"---\nmodel: {Models.GPT_4_TURBO.value.name}\n---"
        if system_prompt != "":
            md = add_message(md, "system", system_prompt)
        md = add_message(md, "user", user_prompt)
        file.write_text(md)
    elif user_prompt != "":
        md = file.read_text()
        md = add_message(md, "user", user_prompt)
        file.write_text(md)

    while True:
        md = file.read_text()
        chat = parse_chat(md)
        metadata = parse_metadata(md)
        model_name = metadata.get("model")
        model = (
            Models.get_by_name(model_name)
            if model_name
            else Models.get_from_env_or_default()
        )
        last_msg = last_item(chat)
        if last_msg is not None and last_msg["role"] == "user":
            console.clear()
            model_options = remove_none_values({**metadata, "model": None})
            answer = print_stream(model.stream(chat, **model_options), render_markdown)
            md = add_message(md, "assistant", answer)
            md = add_message(md, "user", "")
            file.write_text(format_markdown(md))
            cancel = (
                console.input(f"[{COLOR_GRAY_1}]Continue? [Y,n]: [/]").lower() == "n"
            )
            if cancel:
                break
        else:
            result = subprocess.call([editor, file])
            if result != 0:
                print_error(f"Failed to open the editor. Error code: {result}")
                sys.exit(1)

            md = file.read_text()
            last_msg = last_item(parse_chat(md))
            if last_msg is None or last_msg["role"] != "user":
                print_step("Last message is not of role 'user'. Exiting...")
                break


class Metadata(TypedDict):
    model: NotRequired[Optional[str]]
    max_tokens: NotRequired[Optional[int]]
    temperature: NotRequired[Optional[float]]
    top_p: NotRequired[Optional[float]]
    presence_penalty: NotRequired[Optional[float]]


def parse_metadata(md: str) -> Metadata:
    parts = re.split(r"^---\n", md, flags=re.RegexFlag.MULTILINE)
    if len(parts) >= 2:
        front_matter = yaml.safe_load(parts[1])
        return front_matter
    else:
        return {}


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


def add_message(md: str, role: str, message: str) -> str:
    role_with_message = f"{format_role(role)}\n{message}"
    md = md.strip()
    if md != "":
        role_with_message = f"\n\n{role_with_message}"
    md += role_with_message
    return md


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
