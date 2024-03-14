import logging
import shlex
import subprocess
import sys
from typing import Optional, Tuple

logging.basicConfig(level=logging.INFO)


def docs(ignore_cache: bool):
    """
    Build tawa's documentation.

    Args:
        ignore_cache: If ``True``, do not leverage the cache when building
            docs. This will be slower than using the cache but can help
            avoid some errors the builder may encounter when the changes made
            to documentation differ greatly from the content of the cache.
    """
    command = "sphinx-build {args} docs/source docs/build"
    args = [
        "-W",  # Treat warnings as errors.
    ]
    if ignore_cache:
        args.append("-E")
    command = command.format(args=" ".join(args))
    run_subproc_command(command)


def format_package(check: bool = False):
    """Run formatting through ruff with settings in top level pyproject."""
    command = "ruff format"
    if check:
        command = command + " --check"
    command = command + " ."
    run_subproc_command(command)


def lint(fix: bool = False):
    """Run linting through ruff with settings in top level pyproject."""
    command = "ruff check"
    if fix:
        command = command + " --fix"
    command = command + " ."
    run_subproc_command(command)


def test(path: list[str]):
    """
    Run tawa's tests. This uses pytest, runs each test in its own subprocess
    via the ``forked`` plugin, and controls the random seed and the order tests
    are run in via the ``randomly`` plugin.

    Args:
        path: A list of zero or more files or directories to run ``pytest``
            on. This corresponds to the ``[file_or_dir]`` variadic ``pytest``
            argument.
    """
    command_parts = ["pytest"]

    # Run each test in its own process.
    command_parts.extend(["--forked"])

    # Fix the random seed and always run tests in the same order.
    command_parts.extend([f"--randomly-seed={0xa455}", "--randomly-dont-reorganize"])

    command_parts.extend(path)

    run_subproc_command(" ".join(command_parts))


def type_check():
    """Run type checking with mypy and settings in mypy.ini"""
    command = "mypy ."
    run_subproc_command(command)


def run_subproc_command(
    command_str: str,
    exit_on_failure: bool = True,
    exit_on_success: bool = True,
) -> Tuple[Optional[subprocess.CompletedProcess], str]:
    """Run suprocess command in standard piping

    Args:
        command_str (str): The command to run in subshell. Needs to be
            in one string format, will be split internally.
        exit_on_failure (bool): Flag for exiting the entire python process on
            command failure.
        exit_on_success (bool): Flag for exiting the entire python process on
            command success. If false returns the subprocess output.

    Raises:
        RuntimeError: On RuntimeError raise the entire python process exits in
            exit_on_failure is true, otherwise raises error.

    Returns:

    """
    ret = None
    try:
        ret = subprocess.run(
            shlex.split(command_str),
            shell=False,
            check=False,
            capture_output=False,
        )
        if ret.returncode != 0:
            raise RuntimeError("Non 0 exit code on command.")
        logging.info("Command successful")
        if exit_on_success:
            sys.exit(0)
        return ret, "Process exited successfully"

    except RuntimeError:
        error = "Unknown error, no return"
        logging.warning("Failed command.")
        if exit_on_failure:
            sys.exit(1)
        return ret, error
