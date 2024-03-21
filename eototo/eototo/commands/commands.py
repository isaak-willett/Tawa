import getpass
import shlex
import sys
from pwd import getpwnam
from typing import List, Tuple

import click

from eototo.docker.docker_utils import (
    build_user_env_docker_image,
    build_base_env_docker_image,
    get_user_image,
    get_base_image,
    run_generic_command,
)
from eototo.utils.environment import get_aws_creds


def build_base_command(
    additional_docker_build_args: List[Tuple[str, str]],
    buildx: bool,
    forward_artifactory_creds: bool,
    quiet: bool,
    runtime_environment: str,
) -> None:
    """Build the base image in runtime dir if it exists.

    Args:
        additional_docker_build_args (List[Tuple[str, str]]): Additional arbitrary docker build args
        buildx (bool): Use buildx or not
        forward_artifactory_creds (bool): To forward artifactory secrets to build through docker secrets
        quiet (bool): Build quiet flag
        runtime_environment (str): Environment for which to build image
    """
    build_base_env_docker_image(
        build_args=dict(additional_docker_build_args),
        buildx=buildx,
        forward_artifactory_creds=forward_artifactory_creds,
        image=get_base_image(runtime_environment=runtime_environment),
        quiet=quiet,
        runtime_environment=runtime_environment,
    )


def build_command(
    additional_docker_build_args: List[Tuple[str, str]],
    buildx: bool,
    forward_artifactory_creds: bool,
    quiet: bool,
    runtime_environment: str,
) -> None:
    """Build the project image.

    Args:
        additional_docker_build_args (List[Tuple[str, str]]): Additional arbitrary docker build args
        buildx (bool): Use buildx or not
        forward_artifactory_creds (bool): To forward artifactory secrets to build through docker secrets
        quiet (bool): Build quiet flag
        runtime_environment (str): Environment for which to build image
    """
    build_user_env_docker_image(
        build_args=dict(additional_docker_build_args),
        buildx=buildx,
        forward_artifactory_creds=forward_artifactory_creds,
        image=get_user_image(runtime_environment=runtime_environment),
        quiet=quiet,
        runtime_environment=runtime_environment,
    )


def get_user_id_group_id() -> Tuple[int, int]:
    """Get current user group id and user id."""
    user = getpwnam(getpass.getuser())
    return user.pw_uid, user.pw_gid


def docs_command(ignore_cache: bool, read_write: bool, runtime_environment: str, quiet: bool) -> None:
    """
    Build tawa's docs.

    Args:
        ignore_cache: If ``True``, ignore the cache when building documentation.
            This takes longer than using the cache, but sometimes if docs changes
            differ largely from the cache, the documentation builder will
            encounter errors that can only be avoided by ignoring the cache.
        read_write (bool): Whether to mount container with read write
        runtime_environment (str): Environment to run inside
        quiet (bool): Build quiet flag
    """
    user_id, group_id = get_user_id_group_id()

    command = ["tawa-inner-cli", "docs"]
    if ignore_cache:
        command.append("--ignore-cache")

    ret_code = run_generic_command(
        entrypoint_args=command,
        quiet=quiet,
        read_write=read_write,
        runtime_environment=runtime_environment,
        user_gid=group_id,
        user_id=user_id,
    )

    if ret_code.returncode != 0:
        click.secho(
            "Failed to build docs",
            bg="black",
            fg="red",
            err=True,
            bold=True,
        )
        sys.exit(1)
    click.secho("Built docs successfully", bg="blue", fg="green")
    sys.exit(0)


def exec_command(
    build_buildx: bool,
    command: str,
    gpus: bool,
    interactive: bool,
    port_aws_creds: bool,
    read_write: bool,
    root: bool,
    runtime_environment: str,
    quiet: bool,
) -> None:
    """Run user provided command in tawa runtime.

    Args:
        build_buildx (bool): Whether to use buildx
        command (str): command to run in chosen runtime
        gpus (bool): run command with gpus attached
        interactive (bool): run the docker command in interactive
        port_aws_creds (bool): Whether to port host aws creds to container
        read_write (bool): whether to mount volume as read write
        root (bool): whether to pass root user access or not
        runtime_environment (str): Environment to run inside
        quiet (bool): Build quiet flag
    """
    user_id, group_id = get_user_id_group_id()

    env_vars = get_aws_creds() if port_aws_creds else {}

    ret_code = run_generic_command(
        build_buildx=build_buildx,
        entrypoint_args=shlex.split(command),
        env_vars=env_vars,
        gpus=gpus,
        interactive=interactive,
        quiet=quiet,
        read_write=read_write,
        root=root,
        runtime_environment=runtime_environment,
        user_gid=group_id,
        user_id=user_id,
    )

    if ret_code.returncode != 0:
        click.secho(
            f"Failed command: {command}",
            bg="black",
            fg="red",
            err=True,
            bold=True,
        )
        sys.exit(1)
    click.secho(f"Successfully ran command: {command}", bg="blue", fg="green")


def lint_command(
    build_buildx: bool,
    fix: bool,
    read_write: bool,
    runtime_environment: str,
    quiet: bool,
) -> None:
    """Run lint command inside runtime environment container

    Args:
        build_buildx (bool): Whether to use buildx
        fix (bool): Fix the lint errors or not
        read_write (bool): Whether to mount with read write
        runtime_environment (str): Environment to run inside
        quiet (bool): Build quiet flag
    """
    user_id, group_id = get_user_id_group_id()

    command = ["tawa-inner-cli", "lint"]
    if fix:
        command.append("--fix")

    ret_code = run_generic_command(
        build_buildx=build_buildx,
        entrypoint_args=command,
        quiet=quiet,
        read_write=read_write,
        runtime_environment=runtime_environment,
        user_gid=group_id,
        user_id=user_id,
    )

    if ret_code.returncode != 0:
        click.secho(
            "Failed linting",
            bg="black",
            fg="red",
            err=True,
            bold=True,
        )
        sys.exit(1)
    click.secho("Ran linting successfully", bg="blue", fg="green")
    sys.exit(0)


def format_command(
    build_buildx: bool,
    check: bool,
    quiet: bool,
    read_write: bool,
    runtime_environment: str,
) -> None:
    """Run the format command inside the chosen runtime container.

    Args:
        build_buildx (bool): Whether to use buildx
        quiet (bool): Build quiet flag
        read_write (bool): Run container with read write mounting
        runtime_environment (str): Runtime container to run inside
    """
    user_id, group_id = get_user_id_group_id()

    entrypoint_args = ["tawa-inner-cli", "format"]
    if check:
        entrypoint_args.append("--check")

    ret_code = run_generic_command(
        build_buildx=build_buildx,
        entrypoint_args=entrypoint_args,
        quiet=quiet,
        read_write=read_write,
        runtime_environment=runtime_environment,
        user_gid=group_id,
        user_id=user_id,
    )

    if ret_code.returncode != 0:
        click.secho(
            "Failed formatting",
            bg="black",
            fg="red",
            err=True,
            bold=True,
        )
        sys.exit(1)
    click.secho("Ran formatting successfully", bg="blue", fg="green")
    sys.exit(0)


def test_command(
    build_buildx: bool,
    gpus: bool,
    runtime_environment: str,
    quiet: bool,
    path: List[str],
) -> None:
    """
    Run tawa's tests.

    Args:
        build_buildx: Whether to use buildx for docker
        gpus: Whether to run test docker command with gpus enabled
        runtime_environment: Runtime environment to run commands within
        quiet: Run in quiet mode without docker output
        path: A list of one or more files or directories to run ``pytest``
            on. This corresponds to the ``[file_or_dir]`` variadic ``pytest``
            argument.
    """
    user_id, group_id = get_user_id_group_id()

    entrypoint = ["tawa-inner-cli", "test"]
    for f_or_d in path:
        entrypoint.extend(["--path", f_or_d])

    ret_code = run_generic_command(
        build_buildx=build_buildx,
        entrypoint_args=entrypoint,
        gpus=gpus,
        quiet=quiet,
        runtime_environment=runtime_environment,
        user_gid=group_id,
        user_id=user_id,
    )

    if ret_code.returncode != 0:
        click.secho(
            "One or more tests failed",
            bg="black",
            fg="red",
            err=True,
            bold=True,
        )
        sys.exit(1)
    click.secho("Tests ran successfully", bg="blue", fg="green", bold=True)


def type_check_command(build_buildx: bool, runtime_environment: str, quiet: bool) -> None:
    """Run type checking through tawa inner cli.

    Args:
        build_buildx (bool): Whether to use buildx for docker
        runtime_environment (str): Runtime environment to run commands within
        quiet (bool): Run in quiet mode without docker output
    """
    user_id, group_id = get_user_id_group_id()

    ret_code = run_generic_command(
        build_buildx=build_buildx,
        entrypoint_args=["tawa-inner-cli", "type-check"],
        quiet=quiet,
        runtime_environment=runtime_environment,
        user_gid=group_id,
        user_id=user_id,
    )

    if ret_code.returncode != 0:
        click.secho(
            "Failed type checking",
            bg="black",
            fg="red",
            err=True,
            bold=True,
        )
        sys.exit(1)
    click.secho("Ran type checking successfully", bg="blue", fg="green", bold=True)
    sys.exit(0)
