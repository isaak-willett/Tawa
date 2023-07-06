import click


env_option = click.option(
        "--environment", "-env", "environment", default="default", type=str,
        help="Runtime environment for commands."
    )


option_image_name = click.option(
    "--docker-image-name", "-din", "docker_image_name", default="eototo", type=str,
    help = "Name of built docker image."
)


option_image_version = click.option(
    "--image-version", "-iv", "image_version", default="latest", type=str,
    help="Built image version"
)

option_verbose = click.option(
    "--verbose", "-v", "verbose", type=bool, default=False, is_flag=True,
    help="Output console logs from the command"
)