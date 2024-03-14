"""tawa Inner CLI is a package that directly operates on the host machine and
enables all commands for users and developers to run. This is the direct entry point
for this tooling. This represents a pathway for users to interact with tawa and manage
their own workflows.
"""

import click

from tawa import __version__ as __version__
from tawa.tawa_inner_cli.commands.commands import docs, format_package, lint, test, type_check
from tawa.tawa_inner_cli.commands.utils.options import (
    option_docs_ignore_cache,
    option_format_check,
    option_lint_fix,
    option_test_pytest_path,
)


@click.group(help="tawa cli tools for running internal commands")
@click.version_option(
    version=__version__,
    prog_name="tawa Internal",
)
@click.pass_context
def tawa_cli(ctx: click.Context):
    """tawa cli internal entry point.

    Args:
        ctx (click.Context): click context for command group
    """
    pass


@click.command(name="docs", help="Build tawa's docs")
@option_docs_ignore_cache
def cmd_docs(ignore_cache: bool):
    """
    Build tawa's docs.

    Args:
        ignore_cache: If ``True``, do not use the cache when building
        documentation. This is slower than using the cache but can help
        avoid problems the builder may encounter if the local change to
        docs differs greatly from the content of the cache.
    """
    docs(ignore_cache)


@click.command(name="format", help="Run formatting")
@option_format_check
def cmd_format(check: bool = False) -> None:
    """Run tawa-inner-cli format.

    Args:
        check (bool, optional): Check formatting without fixing the files. Defaults to False.
    """
    format_package(check=check)


@click.command(name="lint", help="Run linters")
@option_lint_fix
def cmd_lint(fix: bool = False):
    """Run tawa-inner-cli lint.

    Args:
        fix (bool): whether to fix linting errors or not. Defaults to False
    """
    lint(fix=fix)


@click.command(name="test", help="Run tawa's tests.")
@option_test_pytest_path
def cmd_test(path: list[str]):
    """
    Run tawa's tests.

    Args:
        path: A list of zero or more files or directories to run ``pytest``
            on. This corresponds to the ``[file_or_dir]`` variadic ``pytest``
            argument.
    """
    test(path)


@click.command(name="type-check", help="Run type checking")
def cmd_type_check():
    """Run tawa-inner-cli type checking."""
    type_check()


tawa_cli.add_command(cmd_docs)
tawa_cli.add_command(cmd_format)
tawa_cli.add_command(cmd_lint)
tawa_cli.add_command(cmd_test)
tawa_cli.add_command(cmd_type_check)
