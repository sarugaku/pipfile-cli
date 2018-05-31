import invoke


@invoke.task()
def build(ctx):
    """Build the package into distributables.

    This will create two distributables: source and wheel.
    """
    ctx.run(f'python setup.py sdist bdist_wheel')


@invoke.task()
def clean(ctx):
    """Clean previously built package artifacts.
    """
    ctx.run(f'python setup.py clean')


@invoke.task(pre=[clean, build])
def upload(ctx, repo):
    """Upload the package to an index server.

    This implies cleaning and re-building the package.

    :param repo: Required. Name of the index server to upload to, as specifies
        in your .pypirc configuration file.
    """
    ctx.run(f'twine upload --repository="{repo}" dist/*')
