import click


option_docker_progress = click.option(
    "--docker-progress", '-dp', "docker_progress", type=str, default="auto",
    help="Docker progress console output option"
)


option_runtime_environment = click.option(
    "--runtime-environment", "-env", "runtime_environment", type=str, default="cuda12",
    help="Environment to run command within"
)