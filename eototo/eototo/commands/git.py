import subprocess
from pathlib import Path
from typing import List


def get_repo_name() -> str:
    """Get the name of the current repo

    Returns:
        str: Name of the current repo
    """
    return Path(get_repo_url()).stem


def get_repo_url() -> str:
    """Gets the network url of the current repo

    Returns:
        str: Url of the repo
    """
    cmd = ["git", "config", "--get", "remote.origin.url"]
    return _get_str_output(cmd)


def _get_str_output(cmd: List[str]) -> str:
    """Output from a standard subprocess command

    Args:
        cmd (List[str]): Command to check output

    Returns:
        str: Output in str format
    """
    return subprocess.check_output(cmd, universal_newlines=True).strip()
