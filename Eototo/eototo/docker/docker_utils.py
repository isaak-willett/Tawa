import os
import subprocess
from typing import Dict, List, Optional

import eototo.utils.common as common


def build_dockerfile_from_path(
    image: str,
    dockerfile_path: str,
    docker_progress: str = "auto",
    quiet: bool = False,
    cache_from: Optional[str] = None,
    build_args: Optional[Dict[str, str]] = None,
):
    command = ["docker", "build", "-t", image, "--progress", docker_progress]
    
    if cache_from is not None:
        command.extend(["--cache-from", cache_from])

    # https://docs.docker.com/engine/reference/commandline/build/#set-build-time-variables---build-arg
    if build_args:
        for (k, v) in build_args.items():
            command.extend(["--build-arg", "{}={}".format(k, v)])

    # https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#pipe-dockerfile-through-stdin
    command.extend(["-f ", dockerfile_path, "."])

    stdout_redirect = subprocess.DEVNULL if quiet else None
    command = " ".join(command)
    subprocess.run(command, stdout=stdout_redirect, check=True, shell=True)


def build_user_env_docker_image(
    image: str,
    build_args: Optional[Dict[str, str]] = None,
    cache_from: Optional[str] = None,
    docker_progress: str = "auto",
    quiet: bool = False,
    runtime_environment: str = 'cuda12',
):
    docker_file_path = grab_dockerfile_path_env(runtime_environment)
    build_dockerfile_from_path(
        build_args=build_args,
        cache_from=cache_from,
        dockerfile_path=docker_file_path,
        docker_progress=docker_progress,
        image=image,
        quiet=quiet,
    )


def get_user_image(image_version: str = "latest") -> str:
    return f"tawa-{os.environ.get('RUNTIME_ENVIRONMENT', 'cuda12')}:{image_version}"


def grab_dockerfile_path_env(
    runtime_environment: str
):
    expected_runtime_path = os.path.join(os.getcwd(), common.ENVIRONMENT_WELLKNOWN_LOC)
    expected_runtime_path = os.path.join(expected_runtime_path, runtime_environment, "Dockerfile.project")
    if not os.path.exists(expected_runtime_path):
        raise FileExistsError(f"For env: {runtime_environment}, a Dockerfile.project file must exist at f{expected_runtime_path}")
    return expected_runtime_path


def run_generic_command(
    build: bool = True,
    check: bool = False,
    display_cmd: bool = True,
    docker_progress: str = "auto",
    entrypoint_args: List[str] = [],
    image: str = get_user_image(),
    runtime_environment: str = 'default'
):
    if build:
        build_user_env_docker_image(
            docker_progress=docker_progress,
            image=get_user_image(),
            runtime_environment=runtime_environment
        )

    entrypoint_args = [] if entrypoint_args is None else entrypoint_args
    docker_commands = ["docker", "run"] + [image] + entrypoint_args
    if display_cmd:
        print("> Running docker command: \"{}\"".format(' '.join(docker_commands)))
    return subprocess.run(
        docker_commands,
        check=check,
    )
