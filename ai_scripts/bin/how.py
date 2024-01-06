#!/usr/bin/env python3
import argparse
import os
import pyperclip

from ai_scripts.lib.logging import print_stream, render_syntax
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
    args = parser.parse_args()
    prompt = args.task
    shell = os.getenv("SHELL") or "sh"
    answer = Agent(
        model=Models.get_from_env_or_default(),
        system_prompt=(
            "You are an AI working as a shell. You are prompted with a task and "
            "you are ONLY responding with a shell command to execute that task "
            f"(targeting `{shell}`)."
            "\n\nPlease AVOID COMMENTARY OUTSIDE OF THE SNIPPET RESPONSE.\n\n"
            "DO OMIT THE ``` WRAPPER IN YOUR RESPONSE AND ONLY OUTPUT THE COMMAND."
        ),
        top_p=0.8,
    ).stream(f"How {prompt}")
    answer = print_stream(answer, lambda s: render_syntax(s, "shell"))
    pyperclip.copy(answer)


if __name__ == "__main__":
    main()
