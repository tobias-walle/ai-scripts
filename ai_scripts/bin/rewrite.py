#!/usr/bin/env python3
import argparse
import subprocess
from enum import Enum
from pathlib import Path

import pyperclip

from ai_scripts.lib.agent import Agent
from ai_scripts.lib.logging import (
    print_error,
    print_stream_and_extract_code,
)
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
        "-l",
        "--language",
        help="The target language. If not given it will be guessed by the model.",
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
                "```typescript\n"
                "import { Component, JSX } from 'solid-js';\n"
                "\n"
                "type Props = {\n"
                "  type: 'button' | 'submit';\n"
                "  disabled?: boolean;\n"
                "  onClick?: () => void;\n"
                "  children: JSX.Element;\n"
                "};\n"
                "\n"
                "export const Button: Component<Props> = (props) => {\n"
                "  return (\n"
                "    <button\n"
                "      type={props.type ?? 'button'}\n"
                "      disabled={props.disabled}\n"
                "      onClick={props.onClick}\n"
                "    >\n"
                "      {props.children}\n"
                "    </button>\n"
                "  );\n"
                "};\n"
                "```\n"
            )
        case Format.DIFF:
            format_prompt = "with a diff of the changes following the prompt. Always output a VALID DIFF that can be used by the `patch` command."
            response_example = (
                "```diff\n"
                "@@ -2,6 +2,7 @@\n"
                " \n"
                " type Props = {\n"
                "   type: 'button' | 'submit';\n"
                "+  disabled?: boolean;\n"
                "   onClick?: () => void;\n"
                "   children: JSX.Element;\n"
                " };\n"
                "@@ -10,6 +11,7 @@\n"
                "   return (\n"
                "     <button\n"
                "       type={props.type ?? 'button'}\n"
                "+      disabled={props.disabled}\n"
                "       onClick={props.onClick}\n"
                "     >\n"
                "       {props.children}\n"
                "```\n"
            )

    message = f"prompt: {prompt}\n"
    if language:
        message += f"language: {language}\n"
    message += f"code:\n{code}"
    answer = Agent(
        model=Models.get_from_env_or_default(),
        system_prompt=(
            "You are an AI working as a coding expert."
            f"You are prompted with a prompt and a code snippet and you are ONLY responding {format_prompt}\n"
            "\n"
            "Please comply with the following rules:\n"
            " - If the language is lua, assume it is used in the context of Neovim and doc comments target the lua-language-server"
            " - ANSWER IN MARKDOWN\n"
            " - AVOID COMMENTARY OUTSIDE OF THE SNIPPET\n"
            "\n"
            "\n"
            "EXAMPLE:\n"
            "code:\n"
            "pass the disabled prop\n"
            "\n"
            "code:\n"
            "```typescript\n"
            "import { Component, JSX } from 'solid-js';\n"
            "\n"
            "type Props = {\n"
            "  type: 'button' | 'submit';\n"
            "  onClick?: () => void;\n"
            "  children: JSX.Element;\n"
            "};\n"
            "\n"
            "export const Button: Component<Props> = (props) => {\n"
            "  return (\n"
            "    <button\n"
            "      type={props.type ?? 'button'}\n"
            "      onClick={props.onClick}\n"
            "    >\n"
            "      {props.children}\n"
            "    </button>\n"
            "  );\n"
            "};\n"
            "```\n"
            "\n"
            "RESPONSE:\n" + response_example
        ),
        top_p=0.1,
    ).stream(message)
    answer = print_stream_and_extract_code(answer, language)
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
