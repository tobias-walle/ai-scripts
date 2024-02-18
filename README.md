# AI Scripts

Some cli scripts to interact with chatbots and other ai tools.

> NOTE: I am using the project personally to experiment with AI, so it is very experimental.
> Please use it on your own risk. I will probably add breaking changes to the commands regularly.

You can install the project via:

```sh
poetry install
```

Make the commands globally available via:

```sh
pip install -e .
```

Depending on what models are used you need to provide the following environment variables:

- `OPENAI_API_KEY` for <https://openai.com/>
- `TOGETHER_API_KEY` for <https://api.together.xyz>

You can override the used model using the `MODEL` environment variable (e.g. `gpt-4-1106-preview`, `mistralai/Mistral-7B-Instruct-v0.2`).

The following scripts are currently implemented:

- [how](#how)
- [explain](#explain)
- [explain-code](#explain-code)
- [implement](#implement)
- [rewrite](#rewrite)
- [find-docs](#find-docs)
- [summarize](#summarize)
- [ask-workspace](#ask-workspace)
- [ai-chat](#ai-chat)

## how

```sh
how <prompt>
```

Based on the prompt generates a cli command and copies it to the clipboard.

## explain

```sh
explain <cli-command>
```

Explains a cli command and it's options.


## explain-code

```sh
explain <code>
```

Explains a piece of code by adding comments. If not code is passed as an argument tries to take it from the clipboard.

## implement

```sh
implement <language> <description>
```

Implement a functionality in the given language based on the description.

## rewrite

```sh
rewrite <language> <description> <code?>
```

Rewrite the given code based on the description.

The `code` argument is optional and a clipboard is used as a default.

- `-h, --help` to see all options
- `-f, --file` get the code from a file
- `-o, --format <code|diff>` specifies how the code is formatted.
  If `-f -o diff` is set you are prompted to patch the file directly with the proposed changes.

## find-docs

```sh
find-docs <prompt>
```

Find documentation based on the given prompt.

- `-s, --summary`: Summarizes the docs for you (optional).

## summarize

```sh
summarize <text>
```

Summarize the given text. The text can be also piped via stdin.

## ask-workspace

```sh
ask-workspace <question>
```

Ask a question about the current workspace/folder/codebase. Works best in git repositories.

The following tools need to be installed for this command:

- `eza`: To get informations about the file tree
- `ripgrep`: To search the filesystem for text
- `git`: To search the filesystem for text in a git repository

## ai-chat

```sh
ai-chat <chat-file.md>
```

Chat with the AI and store the chat in a markdown file.
This will open your `$EDITOR`. Every time you save the file, an answer will be generated and added to the file.

The syntax of the chat is the following:

- `[<role>]:` Marks the start of a new message
- You can set options like `model`, `temperature`, `top_p` and `presence_penalty` in the front matter.

Example:

```md
---
model: gpt-4-1106-preview
temperature: 1.3
---

# --- system ---

You are a helpful assistant.

# --- user ---

What is the time?

# --- assistant ---

I'm sorry, but I am unable to provide real-time information or current time as
my capabilities are limited to text-based interactions and I don't have access
to real-time data. However, you can easily check the current time by looking at
the clock on your device or by searching for the current time in your location
on a search engine.
```
