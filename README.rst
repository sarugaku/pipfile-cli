=============================================================
Pipfile-CLI: Command line interface around Pipfile operations
=============================================================

Pipfile-CLI is a command line interface around the Pipfile API. It allows you
to interact with a Pipfile without Pipenv.

The command line interface’s design is based on the three transformation
functions, as described by Sam Boyer in his
`So you want to write a package manager`_ piece:

.. _`So you want to write a package manager`: https://medium.com/@sdboyer/so-you-want-to-write-a-package-manager-4ae9c17d9527

* The user edits Pipfile to add and/or remove packages.
* ``lock`` resolves the abstract dependency set specified in Pipfile, and write
  the resulting concrete dependency set into Pipfile.lock.
* ``sync`` installs the concrete dependency set specified by Pipfile.lock into
  the current environment (with pip).

Only ``sync`` is implemented at the present time.
