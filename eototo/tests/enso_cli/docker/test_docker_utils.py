import subprocess
from unittest.mock import patch
from typing import Any, Dict, List, Optional

import pytest

from eototo.docker.docker_utils import build_dockerfile_from_path, get_repo_name, run_generic_command


@pytest.mark.parametrize(
    "buildx, build_args, cache_from, dockerfile_path, forward_artifactory_creds, image, quiet, expected_command",
    [
        (
            True,
            {},
            None,
            "test/path/to/Dockerfile",
            True,
            "test_image",
            False,
            "docker buildx build -t test_image --network=host -f  test/path/to/Dockerfile .",
        )
    ],
)
def test_build_dockerfile_from_path(
    buildx, build_args, cache_from, dockerfile_path, forward_artifactory_creds, image, quiet, expected_command
):
    with patch("eototo.docker.docker_utils.subprocess.run") as mocked_subproc_run:
        stdout_redirect = subprocess.DEVNULL if quiet else None
        build_dockerfile_from_path(
            buildx=buildx,
            build_args=build_args,
            cache_from=cache_from,
            dockerfile_path=dockerfile_path,
            forward_artifactory_creds=forward_artifactory_creds,
            image=image,
            quiet=quiet,
        )
        mocked_subproc_run.assert_called_with(expected_command, stdout=stdout_redirect, check=True, shell=True)


@pytest.mark.parametrize(
    "build, build_buildx, check, display_cmd, entrypoint_args, env_vars, image, interactive, quiet, read_write, runtime_environment, user_gid, user_id, expected_run_command",
    [
        (
            False,
            False,
            False,
            False,
            [],
            {},
            "",
            False,
            False,
            False,
            "",
            1000,
            1000,
            [
                "docker",
                "run",
                "--rm",
                "--mount",
                "type=bind,source=/opt/tawa,target=/opt/tawa,readonly",
                "-u",
                "1000:1000",
                "",
            ],
        )
    ],
)
def test_run_generic_command(
    build: bool,
    build_buildx: bool,
    check: bool,
    display_cmd: bool,
    entrypoint_args: Optional[List[str]],
    env_vars: Optional[Dict[str, Any]],
    image: str,
    interactive: bool,
    quiet: bool,
    read_write: bool,
    runtime_environment: str,
    user_gid: int,
    user_id: int,
    expected_run_command: List[str],
):
    with patch("eototo.docker.docker_utils.subprocess.run") as mocked_subproc:
        with patch("eototo.docker.docker_utils.build_user_env_docker_image"):
            run_generic_command(
                build=build,
                build_buildx=build,
                check=check,
                display_cmd=display_cmd,
                entrypoint_args=entrypoint_args,
                env_vars=env_vars,
                image=image,
                interactive=interactive,
                quiet=quiet,
                read_write=read_write,
                runtime_environment=runtime_environment,
                user_gid=user_gid,
                user_id=user_id,
            )

            mocked_subproc.assert_called_with(expected_run_command, check=check)


@pytest.mark.parametrize("expected_repo_name", [("tawa")])
def test_get_repo_name(expected_repo_name: str):
    repo_name = get_repo_name()
    assert repo_name == expected_repo_name
