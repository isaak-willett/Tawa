import pkg_resources

import click

from eocli.cli_interface.options import env_option, option_image_name, option_image_version, option_verbose
from eocli.utils.docker_hooks import build_docker_file


__version__ = pkg_resources.get_distribution("eocli").version


@click.group()
@click.version_option(version=__version__, prog_name = "eocli")
@click.pass_context
@env_option
@option_verbose
def eocli(
    ctx: click.Context,
    environment: str,
    verbose: bool
):
    ctx.obj = {'env': environment, 'verbose': verbose}
    print("welcome to eocli")


@click.command(name = "lint", hidden = False)
@click.pass_context
def lint(
    ctx: click.Context,
):
    print(ctx.obj['env'])


@click.command(name = "build", hidden = False)
@click.pass_context
@option_image_name
@option_image_version
def build(
    ctx: click.Context,
    docker_image_name: str,
    image_version: str
):
    build_docker_file(ctx.obj['env'],
                      docker_image_name,
                      image_version,
                      ctx.obj['verbose'])

eocli.add_command(build)
eocli.add_command(lint)