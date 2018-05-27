import sys

import invoke


@invoke.task()
def build(ctx):
    ctx.run(f'"{sys.executable}" setup.py sdist bdist_wheel')
