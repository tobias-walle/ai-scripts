from pathlib import Path

from ai_scripts.lib.sh import run_cmd


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
