RepoGraph
=========

Visualize GitHub submodule graphs with ``dot``.

Installation
------------

.. code-block:: bash

   $ pip install repograph

Usage
-----

.. code-block:: bash

    $ repograph --help
    Usage: repograph [OPTIONS]

      Draw a graph of GitHub submodule relationships.

      Specify roots of the repository graph with `-r <repo>` or `-o <org>`.

      Both -r and -o may be passed multiple times.

    Options:
      --strip-org / --no-strip-org  Strip organization from node labels?
      -l, --layout-program TEXT     Program to use for rendering.  [default: dot]
      -o, --output TEXT             Output Path  [default: repograph.png]
      -g, --org TEXT                GitHub Organization to include
      -r, --repo TEXT               Repository to include
      -t, --token TEXT              GitHub Access Token
      --help                        Show this message and exit.

      Examples:

      # Alternatively, you can pass the token via -t.
      $ export GITHUB_API_TOKEN=<token>

      # Draw a graph rooted at a single repo.
      $ repograph -r <repo>

      # Draw a graph rooted with all the repos in an org.
      $ repograph -o <org>
