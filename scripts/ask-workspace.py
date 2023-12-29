#!/usr/bin/env python3
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
import json

def main():
    prompt = sys.argv[1]
    files = subprocess.getoutput("eza -R --git-ignore --icons=never")
    print(f"> Get relevant keywords")
    answer = ask_mixtral_8_7B(
        [
            {
                "role": "system",
                "content": (
                    "You are an expert programmer and code search expert.\n"
                    "You are given a prompt and are answering with a LIST OF SINGLE WORD, LOWERCASE SEARCH TERMS for finding related content.\n"
                    "As search terms try to include related topics that might be used in related code and documentation.\n"
                    "TRY TO NOT USE TO GENERAL TERMS TO AVOID EXCEEDING THE TOKEN LIMIT.\n"
                    "In the prompt you are also getting a list of files in the project you can use to determine the used technlogies and therefore improve the relevance of the search terms.\n"
                    "Answer with at LEAST 5 AND NOT MORE THAN 10 search terms seperated by space.\n"
                    "DO NOT INCLUDE ANY OTHER TEXT OR EXPLAINATIONS IN YOUR ANSWER!\n"
                ),
            },
            {
                "role": "user",
                # fmt: off
                "content": (
                    f"FILES:\n{files}\n\n"
                    f"PROMPT: {prompt}"
                ),
                # fmt: on
            },
        ]
    )
    keywords = re.split(r"[_\-\s]+", answer.choices[0].message.content or "")[:10]
    # Limit keywords to more relevant ones
    max_tokens_per_keywords = 10_000 / len(keywords)
    keywords = [k for k in keywords if  guess_number_of_tokens(grep_keywords([k])) <= max_tokens_per_keywords]
    print(f"> Search for keywords: {" ".join(keywords)}")
    search = grep_keywords(keywords)
    print(f"> Get relevant files")
    answer = ask_mixtral_8_7B(
        [
            {
                "role": "system",
                "content": (
                    "You are an expert programmer.\n"
                    "You are given a prompt and some context and are answering ONLY with a LIST OF FILE PATHS with content that might be relevant to answer the question.\n"
                    "ONLY ANSWER WITH EXISTING FILE PATHS RELATIVE TO THE ROOT OF THE PROJECT AS A JSON ARRAY!\n"
                    "DO NOT PROVIDE THE DIRECT ANSWER TO THE PROMPT!"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"FILES:\n{files}\n\n"
                    f"SEARCH RESULT RELEVANT KEYWORDS:\n{search}\n\n"
                    f"PROMPT: {prompt}"
                ),
            },
        ]
    )
    try:
        file_paths = json.loads(answer.choices[0].message.content or "")
    except Exception as e:
        print(f"ERROR: Failed to convert to JSON: {answer.choices[0].message.content}")
        raise e
    print(f"> Look into files: {" ".join(file_paths)}")
    files = []
    for file in file_paths:
        if os.path.exists(file):
            files.append(
                {"path": file, "content": subprocess.getoutput(f"head -n 1000 '{file}'")}
            )
    files_context = "\n\n------------------\n\n".join((f"=> CONTENT OF {f["path"]}:\n{f["content"]}" for f in files))
    print(f"> Get final answer")
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
                "content": (
                    f"FILES:\n{files}\n\n"
                    f"SEARCH RESULT RELEVANT KEYWORDS:\n{files}\n\n"
                    f"CONTENT OF SOME RELEVANT FILES:\n{files_context}\n\n"
                    f"PROMPT: {prompt}"
                ),
            },
        ]
    )
    print()
    print(answer.choices[0].message.content)

def grep_keywords(keywords: List[str]) -> str:
    keywords_regex = "|".join((f'"{k}"' for k in keywords))
    return subprocess.getoutput(f'rg -C 1 -i "{keywords_regex}" .')

def guess_number_of_tokens(text: str) -> int:
    return len(re.split(r"\s+", text))

def ask_mixtral_8_7B(
    messages: List[ChatCompletionMessageParam],
) -> ChatCompletion:
    return together_client().chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=messages,
        max_tokens=1024,
    )

def ask_mistral_7B_V2(
    messages: List[ChatCompletionMessageParam],
) -> ChatCompletion:
    return together_client().chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=messages,
        max_tokens=1024,
    )


def ask_gpt_4_turbo(
    messages: List[ChatCompletionMessageParam],
) -> ChatCompletion:
    return openai_client().chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        max_tokens=1024,
    )

def ask_gpt_3_5_turbo(
    messages: List[ChatCompletionMessageParam],
) -> ChatCompletion:
    return openai_client().chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        max_tokens=1024,
    )


def ask_gpt_4(
    messages: List[ChatCompletionMessageParam],
) -> ChatCompletion:
    return openai_client().chat.completions.create(
        model="gpt-4",
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

main()
