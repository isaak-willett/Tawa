import click

option_format_check = click.option(
    "--check",
    "-ch",
    "check",
    is_flag=True,
    default=False,
    help="Check formatting without modifying the files.",
)

option_lint_fix = click.option(
    "--fix",
    "-f",
    "fix",
    is_flag=True,
    default=False,
    help="Fix linting failures.",
)

option_docs_ignore_cache = click.option(
    "--ignore-cache",
    is_flag=True,
    default=False,
)

option_test_pytest_path = click.option(
    "--path",
    multiple=True,
    default=["tawa/tests"],
    show_default=True,
    type=str,
    help="Files or directories to pass to `pytest`. Can be specified multiple times.",
)
