#!/usr/bin/env python3
import os
import sys

from ai_scripts.lib.logging import print_stream, render_markdown
from ai_scripts.lib.agent import Agent
from ai_scripts.lib.model import Models


def main():
    prompt = " ".join(sys.argv[1:])
    answer = Agent(
        model=Models.get_by_name(os.getenv("MODEL", None)),
        system_prompt=(
            "You are an AI working as a shell expert. "
            "You are prompted with a shell command and "
            "you are explaining what it does and all arguments passed to it. "
            "If possible provide the long form of the argument. "
            "Keep the explanations as short as possible.\n"
            "\n"
            "PLEASE USE THIS FORMAT:\n"
            "`<command>` - <short description>\n"
            "\n"
            "<link-to-documentation>\n"
            "\n"
            "- `--<long-form-parameter>, -<shot-form-parameter>`: <description>\n"
            "<...other-parameters-from-the-prompt>\n"
            "\n"
            "`<command-of-prompt>` <full-description-of-example>\n"
            "\n"
            "\n"
            "EXAMPLE BASED ON THE PROMPT `ls -al`:\n"
            "`ls` - List directory contents\n"
            "\n"
            "<https://www.gnu.org/software/coreutils/ls>\n"
            "\n"
            "- `--all, -a`: Include directory entries whose names begin with a dot (`.`)\n"
            "- `--list, -l`: List one file per line with attribute like permissons, group and file size.\n"
            "\n"
            "`ls -al` will display all files and directories, including hidden ones, with detailed information in a long listing format.\n"
        ),
        temperature=0.5,
        top_p=0.3,
        presence_penalty=0.3,
    ).stream(f"How {prompt}")
    print_stream(answer, render_markdown)


if __name__ == "__main__":
    main()
