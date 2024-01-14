#!/usr/bin/env python3
import argparse
import pyperclip

from ai_scripts.lib.logging import (
    print_stream_and_extract_code,
)
from ai_scripts.lib.agent import Agent
from ai_scripts.lib.model import Models


def main():
    parser = argparse.ArgumentParser(
        prog="implement",
        description="Implement something in the defined language based on the prompt",
    )
    parser.add_argument(
        "language",
        help="The target language",
    )
    parser.add_argument(
        "prompt",
        help="The prompt that describes what should be implemented",
    )
    args = parser.parse_args()
    language = args.language
    prompt = args.prompt
    answer = Agent(
        model=Models.get_from_env_or_default(),
        system_prompt=(
            "You are an AI working as a coding expert."
            "You are prompted with a desription and a language and you are ONLY responding with the code that implements that task.\n"
            "\n"
            "Please comply with the following rules:\n"
            " - If the language support it, SPECIFY TYPES for all parameters and the return type"
            "(for example use type hints in python and typescript and type comments in lua or javascript)\n"
            " - If the language is lua, assume it is used in the context of Neovim and doc comments target the lua-language-server"
            " - Prefer simple and short solutions\n"
            " - Avoid creating subprocesses if not strickly necessary\n"
            " - If not specified otherwise, USE LIBRARIES INSTEAD of implementing a custom solution\n"
            " - ANSWER IN MARKDOWN\n"
            " - AVOID COMMENTARY OUTSIDE OF THE SNIPPET\n"
            "\n"
            "\n"
            "EXAMPLE 1:\n"
            "language: python\n"
            "prompt:\n"
            "a function that runs a command and returns stdout as a string\n"
            "\n"
            "REPONSE:\n"
            "```python\n"
            "def run_cmd(cmd: List[str]) -> str:\n"
            '   """Runs the given command and returns stdout"""\n'
            '   return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode("utf-8")\n'
            "```\n"
            "\n"
            "\n"
            "EXAMPLE 2:\n"
            "language: lua\n"
            "prompt:\n"
            "a function to render a popup\n"
            "\n"
            "REPONSE:\n"
            "```lua\n"
            "local function render_popup(opts)\n"
            "  local win_id = vim.api.nvim_open_win(opts.bufnr, true, {\n"
            "    style = 'minimal',\n"
            "    relative = 'editor',\n"
            "    title = opts.title,\n"
            "    border = opts.border,\n"
            "    width = opts.width,\n"
            "    height = opts.height,\n"
            "    row = (vim.o.lines - opts.height) / 2,\n"
            "    col = (vim.o.columns - opts.width) / 2,\n"
            "  })\n"
            "  return win_id\n"
            "end\n"
            "```\n"
        ),
        top_p=0.1,
        presence_penalty=1,
    ).stream(f"language: {language}\n" f"prompt:\n{prompt}\n")
    answer = print_stream_and_extract_code(answer, language)
    pyperclip.copy(answer)


if __name__ == "__main__":
    main()
