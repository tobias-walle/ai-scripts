#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import List
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
)
from openai import OpenAI
import os
import sys
import subprocess
import re
from rich.markdown import Markdown
from rich import print
import json
import os
from pathlib import Path
import tiktoken
from tiktoken.core import Encoding

# TOTAL TOKENS WITH MIXTRAL ARE 32K
TOKEN_LIMIT_FILES = 5000
TOKEN_LIMIT_README = 5000
TOKEN_LIMIT_SEARCH = 10000
TOKEN_LIMIT_FILE_CONTENT = 10000


def main():
    prompt = sys.argv[1]
    content = Content(prompt=prompt)

    print_step("Add file paths to context")
    files = run_cmd(["eza", "-R", "--git-ignore", "--icons=never"])
    content.add_context("FILES", files, TOKEN_LIMIT_FILES)

    print_step("Get relevant keywords")
    answer = ask_mixtral_8_7B(
        [
            {
                "role": "system",
                "content": (
                    "You are an expert programmer and code search expert.\n"
                    "You are given a prompt and are answering with a LIST OF SINGLE WORD, LOWERCASE SEARCH TERMS for finding related content via grep.\n"
                    "As search terms try to include related topics that might be used in related code and documentation.\n"
                    "In the prompt you are also getting a list of files in the project you can use to determine the used technlogies and therefore improve the relevance of the search terms.\n"
                    "Answer with at LEAST 5 AND NOT MORE THAN 10 search terms seperated by space.\n"
                    "DO NOT INCLUDE ANY OTHER TEXT, NOTES OR EXPLAINATIONS IN YOUR ANSWER!\n"
                ),
            },
            {"role": "user", "content": str(content)},
        ]
    )

    readme_path = Path("./README.md")
    if readme_path.exists():
        print_step("Add README.md to context")
        readme_content = readme_path.read_text()
        content.add_context("README", readme_content, TOKEN_LIMIT_README)

    keywords = answer.choices[0].message.content or ""
    keywords = re.sub(r""""'`""", "", keywords)
    keywords = re.split(r"[_\-\s]+", keywords)[:10]
    print_step(f"Search for keywords: [bright_cyan]{" ".join(keywords)}[/bright_cyan]")
    search = ""
    for i, keyword in enumerate(keywords):
        already_used_tokens_search = number_of_tokens(search)
        if already_used_tokens_search >= TOKEN_LIMIT_SEARCH:
            print_status(
                f'Skiping keywords "{" ".join([k for k in keywords[i:]])}" as token limit of {TOKEN_LIMIT_SEARCH} was reached'
            )
            break
        search += limit_tokens(
            grep_keyword(keyword),
            min(3000, TOKEN_LIMIT_SEARCH - already_used_tokens_search),
        )
    content.add_context("SEARCH RESULT RELEVANT KEYWORDS", search, TOKEN_LIMIT_SEARCH)

    print_step("Get relevant files")
    answer = ask_mixtral_8_7B(
        [
            {
                "role": "system",
                "content": (
                    "You are an expert programmer.\n"
                    "You are given a prompt and some context and are answering ONLY with a LIST OF FILE PATHS AS A JSON ARRAY with content that might be relevant to answer the question.\n"
                    "Do not include files that cannot be relevant like images (svg, png, jpeg, etc).\n"
                    "Do not include files that probably contain data or secrets (csv, env, etc.).\n"
                    "ONLY ANSWER WITH EXISTING FILE PATHS RELATIVE TO THE ROOT OF THE PROJECT STARTING WITH ./ AS A JSON ARRAY!\n"
                    "SORT THE FILES BY RELEVANCE. START WITH THE MOST RELEVANT FILE AND END WITH THE LEAST RELEVANT.\n"
                    "ONLY ANSWER WITH THE JSON ARRAY OF FILES, DO NOT ANSWER THE PROMPT DIRECTLY!"
                ),
            },
            {
                "role": "user",
                "content": str(content),
            },
        ]
    )
    answer = answer.choices[0].message.content or ""
    try:
        file_paths = json.loads(answer)
    except Exception:
        print_status("No valid JSON list of files provided")
        print(Markdown(answer))
        return
    print_step(f"Look into files: [bright_cyan]{" ".join(file_paths)}[/bright_cyan]")
    files = []
    for file_path in file_paths:
        if os.path.splitext(file_path)[1] in ("svg", "csv"):
            print_status(f"Ignore {file_path}")
            continue
        file_path = Path(file_path)
        if file_path.exists():
            try:
                file_content = limit_tokens(
                    file_path.read_text(),
                    TOKEN_LIMIT_FILE_CONTENT // len(file_paths),
                )
                files.append(f"=> CONTENT {file_path}:\n{file_content}")
            except Exception:
                print_error(f"Failed to read {file_path}")
    files_context = "\n\n------------------\n\n".join(files)
    content.add_context(
        "CONTENT OF SOME RELEVANT FILES", files_context, TOKEN_LIMIT_FILE_CONTENT
    )

    print_step(f"Get final answer")
    answer = ask_mixtral_8_7B(
        [
            {
                "role": "system",
                "content": (
                    "You are an expert programmer.\n"
                    "You are given a prompt and some context and are answering the question in the prompt based on the given informations.\n"
                    "ANSWER IN MARKDOWN.\n"
                    "EXPLAIN THE SOURCE FOR YOUR ANSWER.\n"
                    "BE CLEAR ABOUT THAT INFORMATION YOU HAVE AND WHAT INFORMATION YOU INTERPRETED BASED ON THE CONTEXT."
                ),
            },
            {
                "role": "user",
                "content": str(content),
            },
        ]
    )
    print()
    answer = answer.choices[0].message.content or ""
    print(Markdown(answer))


@dataclass
class Content:
    prompt: str
    context: List[str] = field(default_factory=list)

    def add_context(self, prefix: str, value: str, token_limit: int):
        limited_value = limit_tokens(value, token_limit)
        if len(limited_value) < len(value):
            print(
                f"- Limited context to {token_limit} (From {number_of_tokens(value)})"
            )
        return self.context.append(f"--- {prefix} ---\n{limited_value}")

    def __str__(self):
        context = "\n\n".join(self.context)
        return f"{context}\n\n--- PROMPT ---\n{self.prompt}"


def print_step(msg: str):
    print(f"[grey74]> {msg}[/]")


def print_status(msg: str):
    print(f"[grey54]- {msg}[/]")


def print_error(msg: str):
    print(f"[bright_red]- ERROR: {msg}[/]")


def grep_keyword(keyword: str) -> str:
    if Path("./.git").exists():
        return run_cmd(
            [
                "git",
                "grep",
                "--max-count=8",
                "--show-function",
                "--heading",
                "--line-number",
                "--break",
                "--ignore-case",
                "--context=1",
                keyword,
                "--",
                ":!.*",
            ]
        )
    else:
        # Fallback to ripgrep if it isn't a git repository
        result = run_cmd(
            [
                "rg",
                "--max-count=8",
                "--heading",
                "--line-number",
                "--smart-case",
                "--context=1",
                "--max-columns=100",
                "--max-columns-preview",
                keyword,
                ".",
            ]
        )
        result.replace("[... omitted end of long line]", "[...]")
        return result


def run_cmd(cmd: List[str]) -> str:
    return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode("utf-8")


def number_of_tokens(text: str) -> int:
    return len(token_encoding().encode(text))


def limit_tokens(text: str, limit: int) -> str:
    encoding = token_encoding()
    tokens = encoding.encode(text)
    tokens = tokens[:limit]
    return encoding.decode(tokens)


def token_encoding() -> Encoding:
    return tiktoken.encoding_for_model("gpt-4-1106-preview")


def ask_mixtral_8_7B(
    messages: List[ChatCompletionMessageParam],
) -> ChatCompletion:
    return together_client().chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=messages,
        max_tokens=1024,
        temperature=1.5,
        top_p=0.9,
        presence_penalty=1.25,
    )


def ask_gpt_4_turbo(
    messages: List[ChatCompletionMessageParam],
) -> ChatCompletion:
    return openai_client().chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        max_tokens=1024,
    )


def together_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("TOGETHER_API_TOKEN"),
        base_url="https://api.together.xyz/v1",
    )


def openai_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )


if __name__ == "__main__":
    main()
