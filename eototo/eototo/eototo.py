"""
tawaCLI is the head on top of the tawa container. In short it provides a path to
running each command withing tawa-inner-cli in the runtime environment. It does this
by creating twin commands on the outside that manage the container aspects of the commands
while calling tawa-inner-cli through the container internal command. This provides the
following.
1. A clear seperation of responsibility between the external and internal (docker, runtime command)
2. Lower maintainance on each tool, each one can be targeted to a specific usage
3. Ease of use for users, they never have to think about containers and only internal commands
4. Consistent usage across all containers and environments.
"""

from typing import List, Tuple

import click
import pkg_resources

from eototo.commands.commands import (
    build_base_command,
    build_command,
    docs_command,
    exec_command,
    format_command,
    lint_command,
    test_command,
    type_check_command,
)
from eototo.utils.cli_options import (
    option_additional_docker_build_arg,
    option_build_buildx,
    option_command,
    option_format_check,
    option_forward_artifactory_creds,
    option_gpus,
    option_ignore_cache,
    option_interactive,
    option_lint_fix,
    option_port_aws_creds,
    option_quiet,
    option_read_write,
    option_root,
    option_runtime_environment,
    option_test_pytest_path,
)


@click.group(help="tawa cli tools for running tawa")
@click.version_option(
    version=pkg_resources.get_distribution("eototo").version,
    prog_name="tawa-cli",
)
@click.pass_context
def eototo(ctx: click.Context):
    """Main CLI entry point for eototo, splits off into command handlers and gets links to internal commands

    Args:
        ctx (click.Context): Context of the click command
    """
    pass


@click.command(name="build", help="Build the runtime environment image.")
@option_additional_docker_build_arg
@option_build_buildx
@option_runtime_environment
@option_forward_artifactory_creds
@option_quiet
def cmd_build(
    additional_docker_build_args: List[Tuple[str, str]],
    build_buildx: bool,
    forward_artifactory_creds: bool,
    runtime_environment: str,
    quiet: bool,
):
    build_command(additional_docker_build_args, build_buildx, forward_artifactory_creds, quiet, runtime_environment)


@click.command(name="build-base", help="Build the base environment image.")
@option_additional_docker_build_arg
@option_build_buildx
@option_forward_artifactory_creds
@option_runtime_environment
@option_quiet
def cmd_build_base(
    additional_docker_build_args: List[Tuple[str, str]],
    build_buildx: bool,
    forward_artifactory_creds: bool,
    runtime_environment: str,
    quiet: bool,
):
    build_base_command(
        additional_docker_build_args, build_buildx, forward_artifactory_creds, quiet, runtime_environment
    )


@click.command(name="exec", help="Execute command in environment container.")
@option_build_buildx
@option_command
@option_gpus
@option_interactive
@option_gpus
@option_port_aws_creds
@option_read_write
@option_root
@option_runtime_environment
@option_quiet
def cmd_exec(
    build_buildx: bool,
    command: str,
    gpus: bool,
    interactive: bool,
    port_aws_creds: bool,
    read_write: bool,
    root: bool,
    runtime_environment: str,
    quiet: bool,
):
    exec_command(build_buildx, command, gpus, interactive, port_aws_creds, read_write, root, runtime_environment, quiet)


@click.command(name="format", help="Format tawa-cli and tawa.")
@option_build_buildx
@option_format_check
@option_quiet
@option_read_write
@option_runtime_environment
def cmd_format(
    build_buildx: bool,
    check: bool,
    quiet: bool,
    read_write: bool,
    runtime_environment: str,
):
    format_command(build_buildx, check, quiet, read_write, runtime_environment)


@click.command(name="lint", help="Lint tawa-cli and tawa.")
@option_build_buildx
@option_lint_fix
@option_read_write
@option_runtime_environment
@option_quiet
def cmd_lint(
    build_buildx: bool,
    fix: bool,
    read_write: bool,
    runtime_environment: str,
    quiet: bool,
):
    lint_command(build_buildx, fix, read_write, runtime_environment, quiet)


@click.command(
    name="test",
    help="Run tawa tests. If no path provided runs tests in first module in target repo in tree, ex: in tawa runs only tests in tawa",
)
@option_build_buildx
@option_gpus
@option_runtime_environment
@option_quiet
@option_test_pytest_path
def cmd_test(
    build_buildx: bool,
    gpus: bool,
    runtime_environment: str,
    quiet: bool,
    path: List[str],
):
    test_command(build_buildx, gpus, runtime_environment, quiet, path)


@click.command(name="type-check", help="Type check tawa and tawa-cli.")
@option_build_buildx
@option_runtime_environment
@option_quiet
def cmd_type_check(build_buildx: bool, runtime_environment: str, quiet: bool):
    type_check_command(build_buildx, runtime_environment, quiet)


@click.command(name="docs", help="Build tawa's docs.")
@option_ignore_cache
@option_read_write
@option_runtime_environment
@option_quiet
def cmd_docs(ignore_cache: bool, read_write: bool, runtime_environment: str, quiet: bool):
    docs_command(ignore_cache, read_write, runtime_environment, quiet)


eototo.add_command(cmd_build)
eototo.add_command(cmd_build_base)
eototo.add_command(cmd_docs)
eototo.add_command(cmd_exec)
eototo.add_command(cmd_lint)
eototo.add_command(cmd_format)
eototo.add_command(cmd_test)
eototo.add_command(cmd_type_check)
