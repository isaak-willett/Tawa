import os
from typing import Optional

import docker


def build_docker_file(
        environment: str,
        tag : Optional[str] = None,
        version: str = "default",
        verbose: bool = False
):
    """Interpret docker env and build image.

    Args:
        environment (str): env to build
        tag (Optional[str], optional): tag for image. Defaults to None.
        version (str, optional): version for image. Defaults to "default".
    """
    client = docker.from_env().api
    docker_file_path = form_env_path(environment)
    with open(docker_file_path, 'rb') as open_docker:
        image = client.build(
            fileobj = open_docker,
            tag = f"{tag}:{version}"
        )
        if verbose:
            for line in image:
                print(line)


def form_env_path(
    environment: str,
    docker_file_name: str = "Dockerfile.user",
) -> str:
    return str(os.path.join(os.getcwd(), "environments", environment, docker_file_name))