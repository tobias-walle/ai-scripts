#!/usr/bin/env python3
import os
import argparse
import pyperclip

from ai_scripts.lib.logging import print
from ai_scripts.lib.agent import Agent
from ai_scripts.lib.model import OpenAIGPT4TurboModel


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="how",
        description="Output a shell command based on the prompt",
    )
    parser.add_argument("prompt", nargs="+")
    args = parser.parse_args()
    prompt = " ".join(args.prompt)
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
    ).prompt(f"How {prompt}")
    print(answer)
    pyperclip.copy(answer)
