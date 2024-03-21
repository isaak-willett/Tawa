import shlex
from subprocess import CompletedProcess
from unittest.mock import patch
from typing import Dict, Tuple

import pytest

import eototo.commands.commands as commands


PATCHED_UID = 0
PATCHED_GID = 0


def _patched_out_auth_function() -> Tuple[int, int]:
    return PATCHED_UID, PATCHED_GID


@pytest.mark.parametrize(
    "additional_docker_build_args, build_buildx, forward_artifactory_creds, quiet, runtime_environment, expected_user_image",
    [
        (
            {"test": "test"},
            True,
            False,
            False,
            "cuda12",
            "tawa-cuda12:latest",
        )
    ],
)
def test_build_command(
    additional_docker_build_args: Dict[str, str],
    build_buildx: bool,
    forward_artifactory_creds: bool,
    quiet: bool,
    runtime_environment: str,
    expected_user_image: str,
):
    # mock out the run_generic_command call
    # will verify the called function signature
    with patch("eototo.commands.commands.build_user_env_docker_image") as patched_build:
        # patch the run object with subprocess good return value to not exit 1 and fail test
        patched_build.return_value = CompletedProcess([], returncode=0)
        commands.build_command(
            additional_docker_build_args=additional_docker_build_args,
            buildx=build_buildx,
            forward_artifactory_creds=forward_artifactory_creds,
            quiet=quiet,
            runtime_environment=runtime_environment,
        )
        patched_build.assert_called_with(
            build_args=additional_docker_build_args,
            buildx=build_buildx,
            forward_artifactory_creds=forward_artifactory_creds,
            image=expected_user_image,
            quiet=quiet,
            runtime_environment=runtime_environment,
        )


@pytest.mark.parametrize(
    "additional_docker_build_args, build_buildx, forward_artifactory_creds, quiet, runtime_environment, expected_user_image",
    [
        (
            {"test": "test"},
            True,
            False,
            False,
            "cuda12",
            "tawa-cuda12-base:latest",
        )
    ],
)
def test_build_base_command(
    additional_docker_build_args: Dict[str, str],
    build_buildx: bool,
    forward_artifactory_creds: bool,
    quiet: bool,
    runtime_environment: str,
    expected_user_image: str,
):
    # mock out the run_generic_command call
    # will verify the called function signature
    with patch("eototo.commands.commands.build_base_env_docker_image") as patched_build:
        # patch the run object with subprocess good return value to not exit 1 and fail test
        patched_build.return_value = CompletedProcess([], returncode=0)
        commands.build_base_command(
            additional_docker_build_args=additional_docker_build_args,
            buildx=build_buildx,
            forward_artifactory_creds=forward_artifactory_creds,
            runtime_environment=runtime_environment,
            quiet=quiet,
        )
        patched_build.assert_called_with(
            build_args=additional_docker_build_args,
            buildx=build_buildx,
            forward_artifactory_creds=forward_artifactory_creds,
            image=expected_user_image,
            quiet=quiet,
            runtime_environment=runtime_environment,
        )


@pytest.mark.parametrize(
    "build_buildx, command, gpus, interactive, port_aws_creds, quiet, read_write, root, runtime_environment, "
    "expected_env_vars, expected_uid, expected_gid",
    [
        (
            True,
            "",
            False,
            False,
            True,
            False,
            False,
            False,
            "cuda12",
            {"AWS_ACCESS_KEY_ID": "", "AWS_DEFAULT_REGION": "", "AWS_SECRET_ACCESS_KEY": "", "AWS_SESSION_TOKEN": ""},
            PATCHED_UID,
            PATCHED_GID,
        )
    ],
)
def test_exec_command(
    build_buildx,
    command,
    gpus,
    interactive,
    port_aws_creds,
    quiet,
    read_write,
    root,
    runtime_environment,
    expected_env_vars,
    expected_uid,
    expected_gid,
):
    # mock out the run_generic_command call
    # will verify the called function signature
    with patch("eototo.commands.commands.run_generic_command") as patched_run:
        # patch the run object with subprocess good return value to not exit 1 and fail test
        patched_run.return_value = CompletedProcess([], returncode=0)

        # patch out here because testing inside docker container borks user groups
        with patch("eototo.commands.commands.get_user_id_group_id", _patched_out_auth_function):
            commands.exec_command(
                build_buildx=build_buildx,
                command=command,
                gpus=gpus,
                interactive=interactive,
                port_aws_creds=port_aws_creds,
                quiet=quiet,
                read_write=read_write,
                root=root,
                runtime_environment=runtime_environment,
            )
            patched_run.assert_called_with(
                build_buildx=build_buildx,
                entrypoint_args=shlex.split(command),
                env_vars=expected_env_vars,
                gpus=gpus,
                interactive=interactive,
                quiet=quiet,
                read_write=read_write,
                root=root,
                runtime_environment=runtime_environment,
                user_gid=expected_gid,
                user_id=expected_uid,
            )


@pytest.mark.parametrize(
    "build_buildx, gpus, runtime_environment, path, quiet, expected_entrypoint_args, expected_uid, expected_gid",
    [
        (
            True,
            False,
            "cuda12",
            "",
            False,
            ["tawa-inner-cli", "test"],
            PATCHED_UID,
            PATCHED_GID,
        )
    ],
)
def test_test_command(
    build_buildx,
    gpus,
    runtime_environment,
    path,
    quiet,
    expected_entrypoint_args,
    expected_uid,
    expected_gid,
):
    # mock out the run_generic_command call
    # will verify the called function signature
    with patch("eototo.commands.commands.run_generic_command") as patched_run:
        # patch the run object with subprocess good return value to not exit 1 and fail test
        patched_run.return_value = CompletedProcess([], returncode=0)

        # patch out here because testing inside docker container borks user groups
        with patch("eototo.commands.commands.get_user_id_group_id", _patched_out_auth_function):
            commands.test_command(
                build_buildx=build_buildx,
                gpus=gpus,
                runtime_environment=runtime_environment,
                path=path,
                quiet=quiet,
            )
            patched_run.assert_called_with(
                build_buildx=build_buildx,
                entrypoint_args=expected_entrypoint_args,
                gpus=gpus,
                quiet=quiet,
                runtime_environment=runtime_environment,
                user_gid=expected_gid,
                user_id=expected_uid,
            )
