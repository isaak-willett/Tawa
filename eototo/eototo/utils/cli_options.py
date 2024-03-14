import click


# pass arbitrary user defined docker run args
option_additional_docker_build_arg = click.option(
    "--additional-docker-build-arg",
    "-adba",
    "additional_docker_build_args",
    default=None,
    help="Arbitrary build args to pass to 'docker build' that are "
    "not be already supported as a formal CLI options. Intended "
    "for CI or power users that need to customize the image build."
    "Example usage:\n"
    "tawa-cli build -adba <your-key> <your-value>",
    multiple=True,
    type=(str, str),
)


# to use docker buildx
option_build_buildx = click.option(
    "--build-buildx",
    "-buildx",
    type=bool,
    default=False,
    is_flag=True,
    help="Use buildx to build image",
)


option_command = click.option(
    "--command",
    "-c",
    "command",
    default="/bin/bash",
    type=str,
    help="Command to run in container. Defaults to /bin/bash.",
)


option_gpus = click.option(
    "--gpus/--no-gpus",
    "gpus",
    default=True,
    help="Run docker command with gpus enabled",
    is_flag=True,
    type=bool,
)


option_interactive = click.option(
    "--interactive",
    "-it",
    "interactive",
    default=False,
    help="Run docker command in interactive mode.",
    is_flag=True,
    type=bool,
)


option_port_aws_creds = click.option(
    "--port-aws-creds",
    "-pac",
    "port_aws_creds",
    type=bool,
    default=True,
    is_flag=True,
    help="Whether to port AWS creds from host to container",
    hidden=True,
)


option_read_write = click.option(
    "--read-write",
    "-rw",
    "read_write",
    type=bool,
    default=True,
    is_flag=True,
    help="Port project with read write permissions. True = port read/write, False = port read. Specify to turn on - Default False",
)


option_root = click.option(
    "--root-run",
    "root",
    default=False,
    help="Run the container as the root user instead of current user. Permissions on any files created by the container must be reset once the container exits.",
    hidden=True,
    is_flag=True,
    type=bool,
)


# what runtime environment to run from
option_runtime_environment = click.option(
    "--runtime-environment",
    "-env",
    "runtime_environment",
    type=str,
    default="cuda12",
    help="Environment to run command within",
)

option_forward_artifactory_creds = click.option(
    "--forward-artifactory-creds",
    type=bool,
    default=True,
    is_flag=True,
    help="Whether to forward Artifactory credentials from host to container",
    hidden=True,
)

option_format_check = click.option(
    "--check",
    "check",
    is_flag=True,
    default=False,
    help="Check formatting without modifying the files.",
)

option_lint_fix = click.option(
    "--fix",
    "-f",
    "fix",
    type=bool,
    default=False,
    is_flag=True,
    help="Run fixing with linting",
)


option_quiet = click.option(
    "--quiet",
    "-q",
    "quiet",
    type=bool,
    default=False,
    is_flag=True,
    help="Run quiet build, runs without stdout from docker run processes",
)


option_ignore_cache = click.option(
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
    help="Files or directories to pass to `pytest`; can be specified multiple times;",
)
