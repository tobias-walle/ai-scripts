#!/usr/bin/env python3
import argparse

import pyperclip

from ai_scripts.lib.logging import print_stream, render_markdown
from ai_scripts.lib.agent import Agent
from ai_scripts.lib.model import Models


def main():
    parser = argparse.ArgumentParser(
        prog="spellcheck", description="spellcheck a given text"
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="The text that should be spellchecked. Defaults to the clipbaord.",
    )
    args = parser.parse_args()
    text = args.text or pyperclip.paste()
    answer = Agent(
        model=Models.get_from_env_or_default(),
        system_prompt=(
            "You are an helpful AI assistance and professional spellchecker.\n"
            "You are given a text and checking the spelling and punctuation of it.\n"
            "You are answering in the language of the given text.\n"
            "You are honoring the following output format:\n"
            "IF THERE ARE ERRORS:\n"
            "<corrected text>\n"
            "\n"
            "- <explanation of correction 1>\n"
            "- <explanation of correction 2>\n"
            "- <explanation of correction 3>\n"
            "\n"
            "OR IF THERE ARE NO ERRORS:\n"
            "Spelling is correct ✅\n"
        ),
        top_p=0.3,
    ).stream(f"{text}")
    print_stream(answer, render_markdown)


if __name__ == "__main__":
    main()
