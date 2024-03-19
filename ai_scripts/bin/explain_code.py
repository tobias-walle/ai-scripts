#!/usr/bin/env python3
import argparse
from typing import Optional

import pyperclip

from ai_scripts.lib.logging import print_stream, render_markdown
from ai_scripts.lib.agent import Agent
from ai_scripts.lib.model import Models


def main():
    parser = argparse.ArgumentParser(
        prog="explain_code",
        description="Explain some piece of code",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        help="An additional prompt or question",
    )
    parser.add_argument(
        "code",
        help="The code that should be explained. Defaults to code in clipboard.",
        nargs="?",
        default=pyperclip.paste(),
    )
    args = parser.parse_args()
    code: str = args.code
    prompt: Optional[str] = args.prompt
    message = ""
    if prompt is not None:
        message += f"{prompt}\n\n"
    message += f"```\n{code}\n```"
    answer = Agent(
        model=Models.get_from_env_or_default(),
        system_prompt=(
            "You are a helpful AI working as an expert programmer. "
            "You are prompted with some code and you will explain what each line does by adding comments to the code.\n"
            "\n"
            "Rules:\n"
            "- You don't need to add comments to each line, focus more parts that are hard to understand.\n"
            "- Detect the language based on the input"
            "- You might get addional instructions or questions at the start of the prompt. In this case prioritize ANSWERING THE QUESTION.\n"
            "- Avoid commentary outside the code snippet. All text outside the snippet will be ignored."
        ),
        top_p=0.3,
    ).stream(f"{message}")
    print_stream(answer, render_markdown)


if __name__ == "__main__":
    main()
