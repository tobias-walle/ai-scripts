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
- [ask-workspace](#ask-workspace)

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

## ask-workspace

```sh
ask-workspace <question>
```

Ask a question about the current workspace/folder/codebase. Works best in git repositories.

The following tools need to be installed for this command:

- `eza`: To get informations about the file tree
- `ripgrep`: To search the filesystem for text
- `git`: To search the filesystem for text in a git repository
