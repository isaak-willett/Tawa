"""
Eototo is an internal/external linker to run simple commands inside Tawa containers.
Eototo facilitates this by developing a bridge through docker commands to build
an external command arbitrarily from a simple internal command.

The power of this comes from Eototo being portable and able to pick up commands that
anyone has written given a few short rules.
"""
import pkg_resources

import click

from eototo.docker.command_linkers import link_internal_commands

@click.group(help="Eototo cli tools for running Tawa")
@click.version_option(version=pkg_resources.get_distribution('eototo').version, prog_name="Eototo")
@click.pass_context
def eototo(ctx: click.Context):
    """Main CLI entry point for eototo, splits off into command handlers and gets links to internal commands

    Args:
        ctx (click.Context): Context of the click command
    """
    pass

link_internal_commands(eototo)