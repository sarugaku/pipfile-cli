=============================================================
Pipfile-Cli: Command line interface around Pipfile operations
=============================================================

Pipfile-Cli is a command line interface around the Pipfile API. It allows you
to interact with a Pipfile without Pipenv.

Currently it only has one functionality: ``pipfile install``. It installs the
content of specified lockfile into the *current environment* (i.e. using the
current pip installation, without creating a virtualenv). It is essentially
``pipenv install --system --deploy`` without all the checks, crafted for those
who already know what they are doing, and want a tool to do exact that.


Todo
====

* Optional check (enabled by default) to make sure the lockfile is up-to-date.
  This would require a way to specify both Pipfile and the lockfile. We will
  probably need to rethink the user interface for that.
