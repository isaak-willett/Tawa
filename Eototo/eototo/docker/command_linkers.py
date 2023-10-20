import getpass
import os
import subprocess
import sys
from typing import Any, Callable, List, Iterable, Union, NamedTuple

import click

import tawa.taw_cli.taw_cli as taw_cli

from eototo.utils.cli_options import option_docker_progress, option_runtime_environment

from eototo.docker.docker_utils import run_generic_command


class DynamicallyParsedInputTuple(NamedTuple):
    """Class to track the name of an option and its value in
       string form to pass as entrypoint arg to docker command
    """
    input_type: str
    input_value: Union[str, List[str]]


def link_internal_commands(
        group_to_link: click.core.Group
) -> None:
    # grab all of the commands that would normally be associated with the group in that
    # local jadoocli, assume all click commands are used (which in general they should be)
    click_commands = [getattr(taw_cli, command) for command
                      in dir(taw_cli) if isinstance(getattr(taw_cli, command), click.core.Command)
                      and not isinstance(getattr(taw_cli, command), click.core.Group)]

    # for all the click commands form them into links to running in the container
    for click_command in click_commands:
        docker_link_command = form_docker_linked_command(click_command)
        group_to_link.add_command(docker_link_command)


def run_linked_command(
    entry_command=str,
    docker_progress: str = "auto", 
    entrypoint_args: List[str] = [],
    runtime_environment: str = 'default'
):
    entrypoint_args = [entry_command] + entrypoint_args
    return run_generic_command(
        docker_progress=docker_progress,
        entrypoint_args=entrypoint_args,
        runtime_environment=runtime_environment
    )


def form_to_docker_input_callback(
    ctx: click.Context,
    param: Union[click.core.Option, click.core.Parameter, click.core.Argument],
    value: Union[str, float, bool, Iterable[str]]
) -> DynamicallyParsedInputTuple:
    """Form the input to this function into a string that can be passed as a
    docker entrypoint arg to local command.

    Args:
        ctx (click.Context): The click context associated with input
        param (Union[click.core.Option, click.core.Parameter, click.core.Argument]):
            The option or agrument to parse value
        value (Union[str, float, bool]): The value to parse into entrypoint arg/args

    Returns:
        DymanicallyParsedInputTuple: The parsed entrypoint arg in the form of a named tuple
    """
    # needed multi returns for proper typing processing
    passable_value: List[str] = []
    input_type = None
    if isinstance(param, click.core.Option):
        passable_value = [param.opts[1]]
        input_type = "option"
        if not param.is_flag:
            passable_value.append(str(value))
    else:
        input_type = "arg"
        if isinstance(value, tuple):
            passable_value = list(value)
    return DynamicallyParsedInputTuple(input_type=input_type, input_value=passable_value)


def options_from_local_options(
    options: List[click.core.Parameter]
) -> Callable[[Any], Any]:
    """Make the linking options to pass input through docker container to local command.

    This function makes the option that links input for each option in the local command.
    It does this by parsing the type out and forcing it to a string input, but allowing
    the same names. This allows us to pass all dynamically parsed options as strings through
    the docker entry point args and infere their types correctly in the internal cli.

    We do this dynamically so we can define the commands only in one place and not need any
    custom linking for any functions. This allows us to be very generic and support all funcs
    regardless of input types.

    We can do this safely because all click options are strings that get parsed in terminal
    anyway. So when we do this process we are maintaining their design paradigm and allowing
    everything to be a string.

    Args:
        options (List[Union[click.core.Option, click.core.Argument]]):
            List of options and arguements to parse

    Returns:
        List[Union[click.core.Option, click.core.Argument]]: The options to add to the dynamic command
    """
    map_to_types = dict(
        array=str,
        number=float,
        string=str,
        bool=bool,
        int=int
    )

    def decorator(f: Any) -> Any:
        for opt_params in reversed(options):
            if isinstance(opt_params, click.Option):
                param_decls = (
                    opt_params.opts[1],
                    opt_params.opts[0],
                    opt_params.name)
                attrs = dict(
                    required=opt_params.required,
                    type=map_to_types.get(
                        str(opt_params.type).lower(), str(opt_params.type).lower())
                )
                attrs['is_flag'] = opt_params.is_flag
                # check to make sure we have a help and a default
                if opt_params.help is not None:
                    attrs['help'] = opt_params.help
                if opt_params.default is not None:
                    # we ignore here, the dict doesn't parse callables in mypy
                    attrs['default'] = opt_params.default   # type: ignore
                # we ignore here, the dict doesn't parse callables in mypy
                attrs['callback'] = form_to_docker_input_callback  # type: ignore

                click.option(*param_decls, **attrs)(f)  # type: ignore
            elif isinstance(opt_params, click.Argument):
                # will always have name but we do this for typing
                if opt_params.name is not None:
                    click.argument(opt_params.name, nargs=opt_params.nargs, callback=form_to_docker_input_callback)(f)
                else:
                    click.argument("args", nargs=opt_params.nargs, callback=form_to_docker_input_callback)(f)
        return f
    return decorator


def form_docker_linked_command(
    taw_cli_command: click.core.Command
) -> click.core.Command:
    """Take a command definition from jadoocli_local and parse.
    Parses a click command from jadoocli local into a callable that
    can then be added as a linking command to jadoocli cloud. The idea
    is that we can let most/all commands that need to be defined in the
    local be defined there. Then just link ourselves by calling through
    the docker container.
    We can infer the inputs, arguments, and names from just the command
    definition. Assuming the local jadoocli_local is installed in the
    container, it's one simple step to pass these to the container when
    we need to call something.
    Args:
        tawa_cli_command (click.Command): command to parse into linking command
    Returns:
        click.Command: command that can call linked command with proper inputs through
        the jadoo docker image.
    """

    @click.command(name=taw_cli_command.name, help=taw_cli_command.help)
    @option_docker_progress
    @option_runtime_environment
    @options_from_local_options(taw_cli_command.params)
    def link_cli_command(
        docker_progress: str,
        runtime_environment: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """Create linked cli command that calls associated command in container
        """
        os.environ['RUNTIME_ENVIRONMENT'] = runtime_environment
        # we need to add tawcli to the entry command to run inside the correct cli
        entry_command = "taw-cli"
        # we need to parse out the entry point args from the options and args on the
        # click function, this is already done because we use callbacks to form them
        # we just need to add them to the run command, with args at the front
        entrypoint_args: List[str] = [taw_cli_command.name]
        for _, parsed_input_tuple in kwargs.items():
            if parsed_input_tuple.input_type == "arg":
                entrypoint_args = parsed_input_tuple.input_value + entrypoint_args
                continue
            else:
                entrypoint_args.extend(parsed_input_tuple.input_value)

        ret_code = run_linked_command(
            docker_progress=docker_progress,
            entry_command=entry_command,
            entrypoint_args=entrypoint_args,
            runtime_environment=runtime_environment,
        )
        # we have to return the permissions back to the user who will always be ubuntu
        subprocess.run(f"sudo chown -R {getpass.getuser()} {os.getcwd()}/*", shell=True, check=True)
        if ret_code.returncode != 0:
            click.secho(f"Failed {link_cli_command.name}", bg="black", fg="red", err=True, bold=True)
            sys.exit(1)
        click.secho(f"Ran {link_cli_command.name} successfully", bg="blue", fg="green")
        sys.exit(0)

    return link_cli_command