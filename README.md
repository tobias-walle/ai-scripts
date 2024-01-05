# AI Scripts

Some cli scripts to interact with chatbots and other ai tools.

You can install the project via:

```sh
poetry install
```

Make the commands globally available via:

```sh
pip install -e .
```

The following scripts are currently implemented:

- [how](#how)
- [explain](#explain)
- [implement](#implement)
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

## implement

```sh
implement <language> <description>
```

Implement a functionality in the given language based on the description.

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
- You can options like `temperature` in the front matter. (TODO)

Example:

```md
[system]:
You are a helpful assistant.

[user]:
What is the time?

[assistant]:
As an artificial intelligence, I don't have feelings or consciousness, so I don't experience states of being in the way humans do.
However I'm here and ready to help you.
How can I assist you today?
```
