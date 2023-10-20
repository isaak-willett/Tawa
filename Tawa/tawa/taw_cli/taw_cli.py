import pkg_resources

import click

from tawa.taw_cli.commands.commands import format, lint

@click.group(help="Tawa cli tools for running internal commands")
@click.version_option(version=pkg_resources.get_distribution('tawa').version, prog_name="Tawa")
@click.pass_context
def taw_cli(ctx: click.Context):
    pass

@click.command(name="format", help="Run linters")
def cmd_format():
    format()

@click.command(name="lint", help="Run linters")
def cmd_lint():
    lint()

taw_cli.add_command(cmd_lint)
taw_cli.add_command(cmd_format)