#!/usr/bin/env python3
from typing import List
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
)
import openai
import os
import sys
import subprocess
import json


def main():
    files = subprocess.getoutput("eza -R --git-ignore -L 4 --icons=never")
    prompt = sys.argv[1]
    messages: List[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": (
                "You are an AI working as a workspace/code expert.\n"
                "You are ONLY answering in JSON in the defined format.\n"
                "You are prompted with a question about the current workspace.\n"
                "\n"
                "To get information about the workspace you can use the following commands. Only ONE COMMAND PER MESSAGE is allowed. DO NOT ADD ANY ADDITIONAL TEXT AND MAKE SURE ALL ANSWERS ARE VALID JSON!."
                "\n"
                '`{ "type": "search", "keywords": <list-of-lowercase-search-terms> }`: '
                "Search the file contents of the whole project based on the given keywords with ripgrep."
                "\n"
                '`{ "type": "content_of", "files": <list-of-file-paths-relative-to-the-workspace-root> }`: '
                "The result will be the given files and their content (limited to the first 100 lines)"
                "\n"
                '`{ "type": "answer", "answer": <your-answer> }`: '
                "Your answer to he given question if you can answer it or are confident you cannot answer it. TRY TO BE CONCISE."
                "\n\n"
                "For example a conversation might look like this:\n"
                "Me: How does the authentication work?"
                'You: {"type": "search", "keywords": ["user", "auth"] }'
                "Me: src/user.py\ndef get_user():\n\n"
                'You: {"type": "content_of", "files": ["src/user.py"] }'
                'Me: src/user.py\ndef get_user():\nprint("Get user")\n\n'
                'You: {"type": "answer", "answer": "The src/user.py file handles the user flow. Currently it just prints something to the console." }'
            ),
        },
        {
            "role": "user",
            "content": (
                f"Files in project (limited to 4 levels):\n{files}\n\nQuestion: {prompt}"
            ),
        },
    ]

    while True:
        output = run_model(messages)
        messages.append(
            ChatCompletionAssistantMessageParam(
                role="assistant", content=output.choices[0].message.content
            )
        )
        answer = output.choices[0].message.content or "<no answer>"
        try:
            parsed_data = json.loads(answer)
        except Exception:
            parsed_data = {"type": "answer", "answer": answer}

        match parsed_data["type"]:
            case "search":
                keywords = parsed_data["keywords"]
                print(f"> Search for keywords: {" ".join(k for k in keywords)}")
                keywords = " ".join((f'"{k}"' for k in keywords))
                search = subprocess.getoutput(f"rg -C 1 {keywords} .")
                messages.append({"role": "user", "content": f"RESULT SEARCH: {search}"})
            case "content_of":
                files = parsed_data["files"]
                print(f"> Look into files: {" ".join(k for k in files)}")
                file_content = ""
                for file in files:
                    if os.path.exists(file):
                        file_content += (
                            f"---------------\nFILE: {file}\nFIRST 100 LINES:\n"
                        )
                        file_content += (
                            subprocess.getoutput("head -n 100 " + file) + "\n"
                        )
                messages.append(
                    {
                        "role": "user",
                        "content": "RESULT CONTENT_OF:" + file_content,
                    }
                )
            case "answer":
                print(parsed_data["answer"])
                break


OPEN_AI_CLIENT = openai.OpenAI(
    api_key=os.getenv("TOGETHER_API_TOKEN"),
    base_url="https://api.together.xyz/v1",
)


def run_model(
    messages: List[ChatCompletionMessageParam],
) -> ChatCompletion:
    return OPEN_AI_CLIENT.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=messages,
        max_tokens=1024,
    )


main()
