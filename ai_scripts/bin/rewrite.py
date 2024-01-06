#!/usr/bin/env python3
import argparse
import subprocess
from enum import Enum
from pathlib import Path

import pyperclip

from ai_scripts.lib.agent import Agent
from ai_scripts.lib.logging import print_error, print_stream, render_syntax
from ai_scripts.lib.model import Models


class Format(Enum):
    CODE = "code"
    DIFF = "diff"


def main():
    parser = argparse.ArgumentParser(
        prog="rewrite",
        description="Rewrite something in the defined language based on the prompt",
    )
    parser.add_argument(
        "language",
        help="The target language",
    )
    parser.add_argument(
        "prompt",
        help="The prompt that describes how the code should be changed",
    )
    parser.add_argument(
        "code",
        help="The code that should be changed",
        nargs="?",
        default=pyperclip.paste(),
    )
    parser.add_argument(
        "-f",
        "--file",
        help="Read input from a file instead of using the code argument",
        default="",
    )
    parser.add_argument(
        "-o",
        "--format",
        help="The format to use",
        type=Format,
        choices=list(Format),
        default=Format.CODE,
    )
    args = parser.parse_args()
    language: str = args.language
    prompt: str = args.prompt
    code: str = args.code
    format: Format = args.format
    file: str = args.file

    if file != "":
        code = Path(file).read_text()

    if code.strip() == "":
        print_error(
            "Please pass the code either as an argument or copy it into the clipboard"
        )
        exit(1)

    format_prompt: str
    response_example: str
    match format:
        case Format.CODE:
            format_prompt = "with the updated the code snippet following the prompt."
            response_example = (
                "def say_hello(name: str):\n"  #
                '    print(f"Hello {name}!")\n'
            )
        case Format.DIFF:
            format_prompt = "with a minimal diff of the changes following the prompt. Only include changes in the diff without the context."
            response_example = (
                "@@ -2,2 +2,2 @@\n"
                '-    print(f"Hello {name}")\n'
                '+    print(f"Hello {name}!")\n'
            )

    answer = Agent(
        model=Models.get_from_env_or_default(),
        system_prompt=(
            "You are an AI working as a coding expert."
            f"You are prompted with a prompt, a language and a code snippet and you are ONLY responding {format_prompt}\n"
            "\n"
            "Please comply with the following rules:\n"
            " - If the language is lua, assume it is used in the context of Neovim and doc comments target the lua-language-server"
            " - AVOID COMMENTARY OUTSIDE OF THE SNIPPET\n"
            " - OMIT THE ``` WRAPPER IN YOUR RESPONSE\n"
            "\n"
            "\n"
            "EXAMPLE:\n"
            "language: python\n"
            "prompt:\n"
            "shout\n"
            "code:\n"
            "def say_hello(name: str):\n"
            '    print(f"Hello {name}")\n'
            "\n"
            "RESPONSE:\n" + response_example
        ),
        temperature=0.8,
        top_p=0.1,
        presence_penalty=1,
    ).stream(f"language: {language}\nprompt:\n{prompt}\ncode:\n{code}\n")
    answer = print_stream(answer, lambda s: render_syntax(s, language))
    if file != "" and format == Format.DIFF:
        if input("Do you want to apply the patch (Y,n): ").lower() != "n":
            apply_patch(file, answer)


def apply_patch(file: str, patch: str):
    if not patch.endswith("\n"):
        patch += "\n"
    p = subprocess.run(
        ["patch", file],
        input=patch.encode("utf-8"),
    )
    if p.returncode != 0:
        print_error(f"Patching failed with exit code {p.returncode}")


if __name__ == "__main__":
    main()
