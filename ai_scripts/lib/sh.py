import subprocess
from typing import List

from ai_scripts.lib.env import is_debbuging
from ai_scripts.lib.logging import print_status


def run_cmd(cmd: List[str]) -> str:
    if is_debbuging():
        cmd_str = " ".join(cmd)
        print_status(f"Run: {cmd_str}")
    return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode("utf-8")
