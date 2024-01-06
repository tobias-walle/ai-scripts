#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import List
import os
import re
import json
from pathlib import Path
import argparse

from ai_scripts.lib.logging import (
    print,
    print_step,
    print_error,
    print_status,
    print_stream,
    render_markdown,
)
from ai_scripts.lib.agent import Agent
from ai_scripts.lib.model import Models
from ai_scripts.lib.fs import grep_keyword
from ai_scripts.lib.sh import run_cmd
from ai_scripts.lib.tokenizing import limit_tokens, number_of_tokens

# TOTAL TOKENS WITH MIXTRAL ARE 32K
TOKEN_LIMIT_FILES = 5000
TOKEN_LIMIT_README = 5000
TOKEN_LIMIT_SEARCH = 10000
TOKEN_LIMIT_FILE_CONTENT = 10000


def main():
    parser = argparse.ArgumentParser(
        prog="ask-workspace",
        description="Ask a question with the current folder as context",
    )
    parser.add_argument(
        "question",
        help="The question that should be answered",
    )
    args = parser.parse_args()
    prompt = args.question
    model = Models.get_from_env_or_default(Models.MIXTRAL_8_7B.value)
    content = Content(prompt=prompt)

    keyword_agent = Agent(
        model=model,
        system_prompt=(
            "You are an expert programmer and code search expert.\n"
            "You are given a prompt and are answering with a LIST OF SINGLE WORD, LOWERCASE SEARCH TERMS for finding related content via grep.\n"
            "As search terms try to include related topics that might be used in related code and documentation.\n"
            "In the prompt you are also getting a list of files in the project you can use to determine the used technlogies and therefore improve the relevance of the search terms.\n"
            "Answer with at LEAST 5 AND NOT MORE THAN 10 search terms seperated by space.\n"
            "DO NOT INCLUDE ANY OTHER TEXT, NOTES OR EXPLAINATIONS IN YOUR ANSWER!\n"
        ),
        top_p=0.1,
    )
    file_paths_agent = Agent(
        model=model,
        system_prompt=(
            "You are an expert programmer.\n"
            "You are given a prompt and some context and are answering ONLY with a LIST OF FILE PATHS AS A JSON ARRAY with content that might be relevant to answer the question.\n"
            "Do not include files that cannot be relevant like images (svg, png, jpeg, etc).\n"
            "Do not include files that probably contain data or secrets (csv, env, etc.).\n"
            "ONLY ANSWER WITH EXISTING FILE PATHS RELATIVE TO THE ROOT OF THE PROJECT STARTING WITH ./ AS A JSON ARRAY!\n"
            "SORT THE FILES BY RELEVANCE. START WITH THE MOST RELEVANT FILE AND END WITH THE LEAST RELEVANT.\n"
            "ONLY ANSWER WITH THE JSON ARRAY OF FILES, DO NOT ANSWER THE PROMPT DIRECTLY!"
        ),
        top_p=0.1,
    )
    final_answer_agent = Agent(
        model=model,
        system_prompt=(
            "You are an expert programmer.\n"
            "You are given a prompt and some context and are answering the question in the prompt based on the given informations.\n"
            "ANSWER IN MARKDOWN.\n"
            "EXPLAIN THE SOURCE FOR YOUR ANSWER.\n"
            "BE CLEAR ABOUT THAT INFORMATION YOU HAVE AND WHAT INFORMATION YOU INTERPRETED BASED ON THE CONTEXT."
        ),
        top_p=0.8,
    )

    print_step("Add file paths to context")
    files = run_cmd(["eza", "-R", "--git-ignore", "--icons=never"])
    content.add_context("FILES", files, TOKEN_LIMIT_FILES)

    print_step("Get relevant keywords")
    answer = keyword_agent.complete(str(content))
    keywords = re.sub(r""""'`""", "", answer)
    keywords = re.split(r"[_\-\s]+", keywords)[:10]
    print_step(f"Search for keywords: [bright_cyan]{' '.join(keywords)}[/bright_cyan]")
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

    readme_path = Path("./README.md")
    if readme_path.exists():
        print_step("Add README.md to context")
        readme_content = readme_path.read_text()
        content.add_context("README", readme_content, TOKEN_LIMIT_README)

    print_step("Get relevant files")
    answer = file_paths_agent.complete(str(content))
    try:
        file_paths = json.loads(answer)
    except Exception as e:
        print_status(f"No valid JSON list of files provided: {e}")
        print(render_markdown(answer))
        return
    print_step(f"Look into files: [bright_cyan]{' '.join(file_paths)}[/bright_cyan]")
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

    print_step("Get final answer")
    answer = final_answer_agent.stream(str(content))
    print()
    print_stream(answer, render_markdown)


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


if __name__ == "__main__":
    main()
