import pathlib

from setuptools import find_packages, setup


# Put everything in setup.cfg, except those that don't actually work?
setup(
    # These really don't work.
    package_dir={'': 'src'},
    packages=find_packages('src'),

    # I don't know how to specify an empty key in setup.cfg.
    package_data={
        '': ['version.txt', 'LICENSE*', 'README*'],
    },

    # I need this to be dynamic.
    version=(
        pathlib.Path(__file__)
        .parent.joinpath('src', 'pipfile_cli', 'version.txt')
        .read_text().strip()
    ),
)
