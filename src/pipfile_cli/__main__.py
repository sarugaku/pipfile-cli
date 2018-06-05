import logging
import pathlib

import click

from ._click import PipfileProjectType


logger = logging.getLogger('')


@click.group()
def cli():
    logging.basicConfig(level=logging.WARNING)


@cli.command()
@click.option(
    '--project', nargs=1, default=pathlib.Path.cwd,
    type=PipfileProjectType(),
)
@click.option(
    '--no-check', is_flag=True, default=False,
)
@click.option(
    '--dev', is_flag=True, default=False,
)
def sync(project, no_check, dev):
    from . import sync

    if no_check:
        click.echo('Skipping lockfile hash check.')

    try:
        lock = sync.get_lock(project, check=(not no_check))
    except sync.LockHashOutOfDateError as e:
        click.echo(
            f'Your Pipfile.lock {e.lock_hash!r} is out of date. '
            f'Expected: {e.pipfile_hash!r}. Aborting.',
            err=True,
        )
        click.get_current_context().exit(1)

    try:
        sync.sync(lock, dev)
    except sync.NothingToDo as e:
        click.echo('No packages not install.')
    except sync.PipError as e:
        click.get_current_context().exit(e.returncode)


if __name__ == '__main__':
    cli()
