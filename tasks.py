import invoke


@invoke.task()
def build(ctx):
    ctx.run(f'python setup.py sdist bdist_wheel')


@invoke.task()
def clean(ctx):
    ctx.run(f'python setup.py clean')


@invoke.task(pre=[clean, build])
def upload(ctx, repo):
    ctx.run(f'twine upload --repository="{repo}" dist/*')
