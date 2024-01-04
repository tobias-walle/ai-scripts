import subprocess
from typing import List


def run_cmd(cmd: List[str]) -> str:
    return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode("utf-8")
