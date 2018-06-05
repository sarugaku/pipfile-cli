import json
import logging
import subprocess
import sys
import tempfile

import requirementslib

from .vendor.pipfile import Pipfile


logger = logging.getLogger('sync')


class LockHashOutOfDateError(ValueError):
    def __init__(self, lock_hash, pipfile_hash):
        super().__init__(lock_hash)
        self.lock_hash = lock_hash
        self.pipfile_hash = pipfile_hash


def get_lock(project, *, check):
    with project.lockfile_path.open() as f:
        lock = json.load(f)
    if not check:
        return lock
    try:
        lock_hash = lock['_meta']['hash']['sha256']
    except (KeyError, TypeError):
        lock_hash = ''
    pipfile_hash = Pipfile.load(project.pipfile_path, inject_env=False).hash
    if pipfile_hash != lock_hash:
        raise LockHashOutOfDateError(lock_hash, pipfile_hash)


class NothingToDo(ValueError):
    pass


class PipError(EnvironmentError):
    def __init__(self, returncode):
        super().__init__(returncode)
        self.returncode = returncode


def sync(lock, dev):
    indexes = lock.get('sources', [])
    packages = lock.get('default', {})
    if dev and 'develop' in lock:
        packages.update(lock['develop'])

    if not packages:
        raise NothingToDo()

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
            raise PipError(e.returncode)
