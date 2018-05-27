import json
import logging
import pathlib
import subprocess
import sys
import tempfile

import click
import requirementslib


DEFAULT_SOURCE = {
    'name': 'pypi',
    'url': 'https://pypi.org/simple',
    'verify_ssl': True,
}

logger = logging.getLogger('')


@click.group()
def cli():
    logging.basicConfig(level=logging.WARNING)


@cli.command()
@click.option(
    '--lockfile', 'lockfile_path', nargs=1, default=None,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    '--dev', is_flag=True, default=False,
)
def install(lockfile_path, dev):
    if lockfile_path:
        lockfile_path = pathlib.Path(lockfile_path)
    else:
        path = pathlib.Path.cwd().joinpath('Pipfile.lock')
        try:
            lockfile_path = path.resolve(strict=True)
        except OSError as e:
            click.echo(f'Could not resolve {path}: {e}', err=True)
            click.get_current_context().exit(1)
    with lockfile_path.open() as f:
        lock = json.load(f)

    indexes = lock.get('sources', [DEFAULT_SOURCE])
    packages = lock.get('default', {})
    if dev and 'develop' in lock:
        packages.update(lock['develop'])

    if not packages:
        click.echo('No packages not install.')
        return

    lines = []
    for name, data in packages.items():
        requirement = requirementslib.Requirement.from_pipfile(
            name=name, indexes=indexes, pipfile=data,
        )
        line = requirement.as_line()
        logger.debug(line)
        lines.append(line)

    with tempfile.NamedTemporaryFile('w+') as requirements_txt:
        requirements_txt.write('\n'.join(lines))
        requirements_txt.flush()
        pip_cmd = [
            sys.executable, '-m',
            'pip', 'install', '-r', requirements_txt.name,
        ]
        logger.info(str(pip_cmd))
        try:
            subprocess.run(pip_cmd, check=True)
        except subprocess.CalledProcessError as e:
            # pip's error message should be enough. Bridge the return code
            # and we should be fine.
            return_code = e.returncode
        else:
            return_code = 0

    if return_code:
        click.get_current_context().exit(return_code)


if __name__ == '__main__':
    cli()
