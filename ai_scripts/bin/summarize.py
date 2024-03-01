#!/usr/bin/env python3
import argparse
import sys
from bs4 import BeautifulSoup

from ai_scripts.lib.logging import print_stream, render_markdown
from ai_scripts.lib.agent import Agent
from ai_scripts.lib.model import Models


def main():
    parser = argparse.ArgumentParser(
        prog="summarize", description="Summarize a given text"
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="The text that should be summarized",
    )
    args = parser.parse_args()
    text_or_html = args.text or sys.stdin.read()
    text = BeautifulSoup(text_or_html, 'html.parser').get_text()
    answer = Agent(
        model=Models.get_from_env_or_default(Models.MIXTRAL_8_7B.value),
        system_prompt=(
            "You are an helpful AI assistance and professional summarizer. "
            "You are given a text and summarize it to its key points in a structured format."
        ),
        top_p=0.3,
    ).stream(f"{text}")
    print_stream(answer, render_markdown)


if __name__ == "__main__":
    main()
