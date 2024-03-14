import logging
import os
import subprocess
import yaml
from typing import Any, Dict, List, Optional

from eototo.commands.git import get_repo_name
from eototo.utils.environment import get_artifactory_creds

logging.basicConfig(level=logging.INFO)


# Standard location of where tawa runtime environments are defined
DEFAULT_ENVIRONMENT_RUNTIME_ENV = "cuda12"
ENVIRONMENT_WELLKNOWN_LOC = "runtime_environments"
WELLKNOWN_BASE_ENV_KEY = "base"
WELLKNOWN_PROJECT_ENV_KEY = "project"


def build_base_env_docker_image(
    image: str,
    buildx: bool = False,
    build_args: Optional[Dict[str, str]] = None,
    cache_from: Optional[str] = None,
    forward_artifactory_creds: bool = True,
    quiet: bool = False,
    runtime_environment: str = DEFAULT_ENVIRONMENT_RUNTIME_ENV,
):
    """Build a base docker image by passing the required files to a lower function.

    This is a wrapper on build_dockerfile_from_path that abstracts getting
    the standard dockerfile location from provided runtime environment.

    Args:
        image (str): The image name to build
        buildx (bool): Whether to use buildx or not
        build_args (Optional[Dict[str, str]], optional): The general build args to provide.
            Defaults to None.
        cache_from (Optional[str], optional): Location to load docker cache from.
            Defaults to None.
        forward_artifactory_creds (bool, optional): To forward artifactory creds on user machine
        quiet (bool, optional): Whether to display docker progress to console.
            Defaults to False.
        runtime_environment (str, optional): The runtime environment where dockerfile is loaded from.
            Defaults to "cuda12".
    """
    docker_file_path = pull_build_location_from_config(runtime_environment, WELLKNOWN_BASE_ENV_KEY)

    if not quiet:
        logging.info(f"Using {runtime_environment} runtime environment")
    build_dockerfile_from_path(
        buildx=buildx,
        build_args=build_args,
        cache_from=cache_from,
        dockerfile_path=docker_file_path,
        image=image,
        forward_artifactory_creds=forward_artifactory_creds,
        quiet=quiet,
    )


def build_dockerfile_from_path(
    image: str,
    dockerfile_path: str,
    buildx: bool = False,
    build_args: Optional[Dict[str, str]] = None,
    cache_from: Optional[str] = None,
    forward_artifactory_creds: bool = True,
    quiet: bool = False,
):
    """Build docker image from provided path and build parameters.

    Args:
        image (str): What image should be named on output
        dockerfile_path (str): Path of docker file to build
        buildx (bool): Whether to use build or not
        build_args (Optional[Dict[str, str]], optional): Build args for docker command.
            Defaults to None.
        cache_from (Optional[str], optional): Optional location to load docker cache.
            Defaults to None.
        forward_artifactory_creds (bool, optional): To forward artifactory creds on user machine
        quiet (bool, optional): Whether to display output to console. Defaults to False.
    """
    # general docker command before inputs
    command = ["docker", "build", "-t", image]
    if buildx:
        command = ["docker", "buildx", "build", "-t", image]

    # required for operations such as `apt install` to correctly resolve URLs
    command.append("--network=host")

    # provide cache location if available
    if cache_from is not None:
        command.extend(["--cache-from", cache_from])

    # additional build args provided generically
    # https://docs.docker.com/engine/reference/commandline/build/#set-build-time-variables---build-arg
    if build_args:
        for k, v in build_args.items():
            command.extend(["--build-arg", f"{k}={v}"])

    # setup environment secret mounting
    # https://docs.docker.com/build/building/secrets/
    # regular build-args are not recommended for secrets handling
    # https://docs.docker.com/reference/dockerfile/#arg
    mount_secrets_env: List[str] = []
    if forward_artifactory_creds:
        artifactory_creds = get_artifactory_creds()
        # we just need the name of the env variable, not the value
        mount_secrets_env.extend(artifactory_creds.keys())

    # docker will automatically use name of the environment variable
    for mount_secret in mount_secrets_env:
        # check if environment variable is set and not zero, otherwise warn
        if mount_secret in os.environ and os.getenv(mount_secret):
            command.extend(["--secret", f"id={mount_secret},env={mount_secret}"])
        else:
            logging.warning("Environment variable %s needed for docker build is not set.", mount_secret)

    # docker file location addition to build
    # https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#pipe-dockerfile-through-stdin
    command.extend(["-f ", dockerfile_path, "."])

    # if quiet redirect the output to the DEVNULL process
    stdout_redirect = subprocess.DEVNULL if quiet else None

    logging.info(f"Building image {image} from path {dockerfile_path}")

    str_command = " ".join(command)

    if not quiet:
        logging.info(f"Docker build command:\n{str_command}")

    subprocess.run(str_command, stdout=stdout_redirect, check=True, shell=True)


def build_user_env_docker_image(
    image: str,
    buildx: bool = False,
    build_args: Optional[Dict[str, str]] = None,
    cache_from: Optional[str] = None,
    forward_artifactory_creds: bool = True,
    quiet: bool = False,
    runtime_environment: str = DEFAULT_ENVIRONMENT_RUNTIME_ENV,
):
    """Build a docker image by passing the required files to a lower function.

    This is a wrapper on build_dockerfile_from_path that abstracts getting
    the standard dockerfile location from provided runtime environment.

    Args:
        image (str): The image name to build
        buildx (bool): Whether to use buildx or not
        build_args (Optional[Dict[str, str]], optional): The general build args to provide.
            Defaults to None.
        cache_from (Optional[str], optional): Location to load docker cache from.
            Defaults to None.
        forward_artifactory_creds (bool, optional): To forward artifactory creds on user machine
        quiet (bool, optional): Whether to display docker progress to console.
            Defaults to False.
        runtime_environment (str, optional): The runtime environment where dockerfile is loaded from.
            Defaults to "cuda12".
    """
    docker_file_path = pull_build_location_from_config(runtime_environment, WELLKNOWN_PROJECT_ENV_KEY)

    if not quiet:
        logging.info(f"Using {runtime_environment} runtime environment")
    build_dockerfile_from_path(
        buildx=buildx,
        build_args=build_args,
        cache_from=cache_from,
        dockerfile_path=docker_file_path,
        forward_artifactory_creds=forward_artifactory_creds,
        image=image,
        quiet=quiet,
    )


def get_base_image(image_version: str = "latest", runtime_environment: str = DEFAULT_ENVIRONMENT_RUNTIME_ENV) -> str:
    """Gets the base image name.

    Standarded naming for the tag on the built image.

    Args:
        image_version (str, optional): Version of image. Defaults to "latest".
        runtime_environment (str, optional): Name of the runtime environment holding the image.
            Defaults to DEFAULT_ENVIRONMENT_RUNTIME_ENV.

    Returns:
        str: The standard fully formed string name of the docker image
    """
    repo_name = get_repo_name()
    return f"{repo_name}-{runtime_environment}-base:{image_version}"


def get_user_image(image_version: str = "latest", runtime_environment: str = DEFAULT_ENVIRONMENT_RUNTIME_ENV) -> str:
    """Gets the user image name.

    Standarded naming for the tag on the built image.

    Args:
        image_version (str, optional): Version of image. Defaults to "latest".
        runtime_environment (str, optional): Name of the runtime environment holding the image.
            Defaults to DEFAULT_ENVIRONMENT_RUNTIME_ENV.

    Returns:
        str: The standard fully formed string name of the docker image
    """
    repo_name = get_repo_name()
    return f"{repo_name}-{runtime_environment}:{image_version}"


def pull_build_location_from_config(runtime_environment: str, file_key: Optional[str] = None) -> str:
    """Pull build environment Dockerfile loc from runtime config

    Args:
        runtime_environment (str): runtime environment to get build file loc
        file_key (str): file key in the runtime env config to pull file

    Returns:
        str: full expected path to build file in runtime_environments
    """
    if file_key is None:
        logging.info("Runtime env file key provided is none, assuming assuming key is project")
        file_key = WELLKNOWN_PROJECT_ENV_KEY

    # load config from well known path
    config_file_path = "runtime_environments/environments.yml"
    with open(config_file_path, "r") as config_buffer:
        config_object = yaml.safe_load(config_buffer)

    # parse through to ensure key is there
    environment_object = config_object["environments"]
    if runtime_environment not in environment_object:
        raise ValueError(f"No {runtime_environment} in {config_file_path}")

    if file_key not in environment_object[runtime_environment]:
        raise ValueError(f"No {file_key} in {runtime_environment} definition in config - {config_file_path}")

    build_file_name = environment_object[runtime_environment][file_key]
    expected_path = f"runtime_environments/{runtime_environment}/{build_file_name}"
    if not os.path.exists(expected_path):
        raise FileExistsError(f"Expected runtime path: {expected_path} does not exist.")

    return expected_path


def run_generic_command(
    build: bool = True,
    build_buildx: bool = False,
    check: bool = False,
    display_cmd: bool = True,
    entrypoint_args: Optional[List[str]] = None,
    env_vars: Optional[Dict[str, Any]] = None,
    gpus: bool = False,
    image: str = get_user_image(),
    interactive: bool = False,
    quiet: bool = False,
    read_write: bool = True,
    root: bool = False,
    runtime_environment: str = "default",
    user_gid: int = 1000,
    user_id: int = 1000,
) -> subprocess.CompletedProcess:
    """Run a generic docker command in a standard way and build if user specified.

    Args:
        build (bool, optional): Flag to build image or not. Defaults to True.
        build_buildx (bool, optional): Flag to build with buildx. Defaults to False.
        check (bool, optional): Flag to ensure process success. Defaults to False.
        display_cmd (bool, optional): Flag to display user command. Defaults to True.
        entrypoint_args (List[str], optional): Entry point args for docker run.
            Defaults to None.
        env_vars (Optional[Dict[str, Any]], optional): Dict of str - Any env vars to pass to container. Defaults to None.
        gpus (bool, optional): Flag to turn on or off gpus. Defaults to False (gpus off).
        interactive (bool, optional): Bool to run command in interactive mode in container. Defaults to False.
        image (str, optional): What image to run docker command on.
            Defaults to get_user_image().
        read_write (bool, optional): Run command with read write mounting. Defaults to False.
        root (bool, optional): Run with root user and group instead of current user. Defaults to False.
        runtime_environment (str, optional): What runtime environment location image file exists in.
            Defaults to "default".
        user_gid (int, optional): User id to mount to container. Defaults to 1000.
        user_id (int, optional): Group id to mount to container. Defaults to 1000.

    Returns:
        subprocess.CompletedProcess: Completed process object
    """
    if entrypoint_args is None:
        entrypoint_args = []

    if build:
        build_user_env_docker_image(
            buildx=build_buildx,
            image=get_user_image(),
            quiet=quiet,
            runtime_environment=runtime_environment,
        )

    # have to add read/write bindings to port changes back to users
    # depends on the read/write enable now, not all commands need this privilege
    entry_point_mounts = []
    target_dir_name = os.path.split(os.getcwd())[1]
    mount_config = f"type=bind,source={os.getcwd()},target=/opt/{target_dir_name}"
    if not read_write:
        mount_config = mount_config + ",readonly"
    entry_point_mounts = [
        "--mount",
        mount_config,
    ]

    interactive_run_args = ["-it"] if interactive else []

    gpu_args = ["--gpus", "all"] if gpus else []

    # mount the current user to not break host machine read write
    entry_point_user = [] if root else ["-u", f"{user_id}:{user_gid}"]

    env_args = []
    # parse the env vars to port
    if env_vars is not None:
        for key, value in env_vars.items():
            env_args.extend(["-e", f"{key}={value}"])

    # docker command assembly
    docker_commands = (
        ["docker", "run", "--rm"]
        + entry_point_mounts
        + entry_point_user
        + env_args
        + gpu_args
        + interactive_run_args
        + [image]
        + entrypoint_args
    )

    # output command if specified
    if display_cmd:
        logging.info('> Running docker command: "{}"'.format(" ".join(docker_commands)))

    return subprocess.run(
        docker_commands,
        check=check,
    )
