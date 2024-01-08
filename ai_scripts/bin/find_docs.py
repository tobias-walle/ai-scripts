#!/usr/bin/env python3
import argparse

from ai_scripts.lib.logging import (
    print_stream,
    render_markdown,
)
from ai_scripts.lib.agent import Agent
from ai_scripts.lib.model import Models


def main():
    parser = argparse.ArgumentParser(
        prog="get-docs",
        description="Find docs of all kinds",
    )
    parser.add_argument(
        "prompt",
        help="The prompt that describes what docs to find",
    )
    parser.add_argument(
        "-s",
        "--summary",
        help="Summarizes the docs for you",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()
    prompt: str = args.prompt
    summary: bool = args.summary

    def if_summary(txt, fallback=""):
        return txt if summary else fallback

    answer = Agent(
        model=Models.get_from_env_or_default(),
        system_prompt=(
            "You are an AI working as a coding and documentation expert. \n"
            "You are prompted with a programming library or method or any other tool "
            "and you are answering "
            + if_summary(
                "with one or multiple urls to the relevant documentation, source code, guides and a short summary.",
                "ONLY with one or more urls to the relevant documentation, source code and guides",
            )
            + "\n"
            "Please comply with the following rules:\n"
            " - If you don't have the documentation link please make this clear in your answer instead of guessing. You might want to add a less specific url instead.\n"
            + if_summary(
                " - Keep the summary very short and focus on the main facts and usage\n"
            )
            + "\n"
            "\n"
            "EXAMPLE:\n"
            "python subprocess.run\n"
            "\n"
            "RESPONSE:\n"
            "- https://docs.python.org/3/library/subprocess.html#subprocess.run\n"
            "- https://github.com/python/cpython/blob/main/Lib/subprocess.py#L510\n"
            "- https://www.digitalocean.com/community/tutorials/how-to-use-subprocess-to-run-external-programs-in-python-3\n"
            "- https://other-relevant-links\n"
            + if_summary(
                "\n"
                "The `subprocess.run()` method in Python is used to run the command described by `args` and wait for the command to complete, returning a `CompletedProcess` instance. A set of parameters can be customized:\n"
                "\n"
                "-  `args`: It is the sequence of program commands and arguments.\n"
                "-  `stdin`, `stdout`, `stderr`: They are used to specify the executed program's input, standard output, and standard error file handles, respectively.\n"
                "-  `capture_output`: If set to true, `stdout` and `stderr` will be captured. This internally sets `stdout=PIPE` and `stderr=PIPE`.\n"
                "-  `shell`: If true, the command will execute in a shell instance.\n"
                "-  `cwd`: It allows you to set the current working directory for the command.\n"
                "-  `timeout`: Can be specified in seconds, killing the subprocess if time expires.\n"
                "-  `check`: If true, a non-zero exit process will raise a `CalledProcessError`.\n"
                "-  `encoding` and `errors`: They define the text encoding and error handling for file objects. If specified, or when `text` is true, the file objects for `stdin`, `stdout`, and `stderr` are opened in text mode.\n"
                "-  `env`: If not None, it must be a dictionary defining the environment variables for the new process.\n"
                "-  `text`: If true, file objects for `stdin`, `stdout` and `stderr` are opened in text mode. Equivalent to `universal_newlines`.\n"
                "\n"
                "The function was introduced in Python 3.5, with the `encoding` and `errors` parameters added in 3.6, `text` and `capture_output` in 3.7, and the behavior for `shell=True` on Windows changed in version 3.12.\n"
            )
        ),
    ).stream(prompt.strip())
    answer = print_stream(answer, render_markdown)


if __name__ == "__main__":
    main()
