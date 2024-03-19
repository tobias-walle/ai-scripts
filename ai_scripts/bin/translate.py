#!/usr/bin/env python3
import argparse
import sys

from ai_scripts.lib.logging import print_stream, render_markdown
from ai_scripts.lib.agent import Agent
from ai_scripts.lib.model import Models


def main():
    parser = argparse.ArgumentParser(
        prog="translate", description="translate a given text"
    )
    parser.add_argument(
        "-l",
        "--language",
        default="english",
        help="The language to translate to",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="The text that should be summarized",
    )
    args = parser.parse_args()
    language = args.language
    text = args.text or sys.stdin.read()
    answer = Agent(
        model=Models.get_from_env_or_default(),
        system_prompt=(
            "You are an helpful AI assistance and professional translater.\n"
            f"You are given a text and translate it to {language}.\n"
            "\n"
            "ONLY OUTPUT THE TRANSLATED TEXT, NO FURTHER DESCRIPTION OR NOTES"
        ),
        top_p=0.3,
    ).stream(f"{text}")
    print_stream(answer, render_markdown)


if __name__ == "__main__":
    main()
