import json
import logging
import pathlib
import subprocess
import sys
import tempfile

import click
import requirementslib

from .vendor.pipfile import Pipfile


DEFAULT_SOURCES = [
    {
        'name': 'pypi',
        'url': 'https://pypi.org/simple',
        'verify_ssl': True,
    },
]

logger = logging.getLogger('')


# Basically a copy of click._compat.filename_to_ui.
def filename_to_ui(value):
    if isinstance(value, bytes):
        fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
        value = value.decode(fs_encoding, 'replace')
    elif sys.version_info[0] >= 3:
        value = (
            value.encode('utf-8', 'surrogateescape')
            .decode('utf-8', 'replace')
        )
    return value


class PipfileProject:

    def __init__(self, path):
        self.path = path

    @property
    def pipfile_path(self):
        return self.path.joinpath('Pipfile')

    @property
    def lockfile_path(self):
        return self.path.joinpath('Pipfile.lock')


class PipfileProjectType(click.Path):

    def __init__(self, **kwargs):
        super().__init__(exists=True, file_okay=False, dir_okay=True, **kwargs)

    def convert(self, val, param, ctx):
        result = pathlib.Path(super().convert(val, param, ctx))
        if not result.joinpath('Pipfile').is_file():
            self.fail(
                f'Directory {filename_to_ui(val)} '
                f'does not contain a Pipfile.',
                param, ctx,
            )
        if not result.joinpath('Pipfile.lock').is_file():
            self.fail(
                f'Directory {filename_to_ui(val)} '
                f'does not contain a Pipfile.lock.',
                param, ctx,
            )
        return PipfileProject(result)


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
def install(project, no_check, dev):
    with project.lockfile_path.open() as f:
        lock = json.load(f)

    if no_check:
        click.echo('Skipping lockfile hash check.')
    else:
        pipfile = Pipfile.load(project.pipfile_path, inject_env=False)
        try:
            lock_hash = lock['_meta']['hash']['sha256']
        except (KeyError, TypeError):
            lock_hash = ''
        pipfile_hash = pipfile.hash
        if pipfile_hash != lock_hash:
            click.echo(
                f'Your Pipfile.lock ({lock_hash}) is out of date. '
                f'Expected: ({pipfile_hash}). Aborting.',
                err=True,
            )
            click.get_current_context().exit(1)

    indexes = lock.get('sources', DEFAULT_SOURCES)
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
