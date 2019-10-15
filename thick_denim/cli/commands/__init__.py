# -*- coding: utf-8 -*-
import os
import sys
import imp
import click
from pathlib import Path
from thick_denim.version import version
from thick_denim.config import ThickDenimConfig
from thick_denim.errors import ThickDenimError

from thick_denim import logs


ui = logs.UIReporter("ThickDenim CLI")


@click.group()
@click.option(
    "--debug/--no-debug", "-d", default=False, help="prints debug information"
)
@click.option(
    "--verbose/--no-verbose",
    "-v",
    default=False,
    help="reports progress of internal calls",
)
def main(debug, verbose):
    """thick-denim command line
    """
    config = ThickDenimConfig()

    debug = debug or config.get_debug_mode()
    verbose = verbose or config.get_verbose_mode()

    logs.set_debug_mode(debug)
    logs.set_verbose_mode(verbose or debug)


@main.command(name="version")
def print_version():
    "prints the version to the STDOUT"
    logs.print(f"thick-denim {version}")


@main.command(name="run", context_settings=dict(ignore_unknown_options=True))
@click.argument("filename")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def run(filename, args):
    "runs the code in the given file"
    filename = Path(filename).expanduser().absolute()
    if not filename.exists():
        print(f"{filename} does not exist")
        raise SystemExit(1)

    config = ThickDenimConfig()
    module_name, ext = os.path.splitext(str(filename))
    meta = imp.find_module(
        module_name, [str(filename.parent)] + list(sys.path)
    )
    mod = imp.load_module(module_name, *meta)

    main = getattr(mod, "main", None)
    if not main:
        print(f'{filename} does not contain a function named "main"')
        raise SystemExit(1)

    if not callable(main):
        print(
            f'{filename} contains "main" but is not a callable function: {main!r}'
        )
        raise SystemExit(1)

    try:
        main(config, args)
    except ThickDenimError as exc:
        logs.print_err(f"{exc.__class__.__name__}: \033[1;31m{exc}")
