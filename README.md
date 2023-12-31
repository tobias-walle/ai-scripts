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

- [ask-workspace](#ask-workspace)

## ask-workspace

```sh
ask-workspace <question>
```

Ask a question about the current workspace/folder/codebase. Works best in git repositories.

The following tools need to be installed for this command:

- `eza`: To get informations about the file tree
- `ripgrep`: To search the filesystem for text
- `git`: To search the filesystem for text in a git repository
