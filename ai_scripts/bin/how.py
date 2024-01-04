#!/usr/bin/env python3
import os
import sys
import pyperclip

from ai_scripts.lib.logging import print_stream
from ai_scripts.lib.agent import Agent
from ai_scripts.lib.model import OpenAIGPT4TurboModel


def main():
    prompt = " ".join(sys.argv[1:])
    shell = os.getenv("SHELL") or "sh"
    answer = Agent(
        model=OpenAIGPT4TurboModel(),
        system_prompt=(
            "You are an AI working as a shell. You are prompted with a task and "
            "you are ONLY responding with a shell command to execute that task "
            f"(targeting `{shell}`)."
            "\n\nPlease AVOID COMMENTARY OUTSIDE OF THE SNIPPET RESPONSE.\n\n"
            "DO OMIT THE ``` WRAPPER IN YOUR RESPONSE AND ONLY OUTPUT THE COMMAND."
        ),
        temperature=0.8,
        top_p=0.8,
        presence_penalty=0.3,
    ).stream(f"How {prompt}")
    answer = print_stream(answer)
    pyperclip.copy(answer)


if __name__ == "__main__":
    main()
