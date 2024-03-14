import subprocess
from pathlib import Path
from typing import List


def get_repo_name() -> str:
    return Path(get_repo_url()).stem

def get_repo_url() -> str:
    cmd = ["git", "config", "--get", "remote.origin.url"]
    return _get_str_output(cmd)

def _get_str_output(cmd: List[str]) -> str:
    return subprocess.check_output(cmd, universal_newlines=True).strip()