#!/usr/bin/env python3
import argparse
import os
import pyperclip

from ai_scripts.lib.logging import print_stream
from ai_scripts.lib.agent import Agent
from ai_scripts.lib.model import Models


def main():
    parser = argparse.ArgumentParser(
        prog="how",
        description="Given a task, returns a shell script that executes the task. "
        "Shell in use is extracted from the SHELL env variable.",
    )
    parser.add_argument(
        "task",
        help="The task that should be executed by the shell script",
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Override the model",
    )
    args = parser.parse_args()
    prompt = args.task
    shell = os.getenv("SHELL") or "sh"
    answer = Agent(
        model=Models.get_by_name(args.model),
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
