import pathlib
import sys

import click


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
