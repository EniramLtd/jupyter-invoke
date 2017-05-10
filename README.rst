==============
Jupyter-Invoke
==============

This package provides an extension to Jupyter notebook server, which enables
executing notebooks non-interactively and obtaining JSON or CSV output with
HTTP requests.

Installation
============

.. code-block:: bash

    pip install git+https://github.com/EniramLtd/jupyter-invoke.git

You can enable the server extension in all new notebook servers by
running

.. code-block:: bash

    jupyter serverextension enable --py jupyter_invoke

You can also enable the extension at command line when you a start
particular server:

.. code-block:: bash

    jupyter notebook --NotebookApp.nbserver_extensions="{'jupyter_invoke':True}"

Alternatively, you can set the variable in a `Jupyter config file`_:

.. code-block:: python

    c = get_config()
    c.NotebookApp.nbserver_extensions = {
        'jupyter_invoke': True,
    }

.. _`Jupyter config file`: http://jupyter-notebook.readthedocs.io/en/latest/config_overview.html

Usage
=====

In a Jupyter notebook, call :func:`jupyter_invoke.response.respond` at the end
of one cell to mark it as providing the invocation output:

.. code-block:: python

    from jupyter_invoke import respond
    a = {'a': [1, 2, 3]}
    respond(a)

This will mark the cell as providing JSON output when querying
``http://<server_address>:<port>/invoke/<path/to/notebook.ipynb>``


Allowing only certain notebooks to be invoked
---------------------------------------------

It is possible to restrict the invocation to only particularly
named notebooks.  There is a configuration parameters
``Invoker.filename_pattern`` which, if specified, matches the end of
the notebook filename (before ``.ipynb``) before allowing the invocation.
Non-matching notebooks are then invisible to the invoke handler.  As an
example, consider the following jupyter configuration file that allows only
files with pattern ``*_invoke.ipynb`` to be invoked:

.. code-block:: python

    c = get_config()
    c.Invoker.filename_pattern = '_invoke'

By default, all notebooks can be invoked.


Using query parameters in invocation
------------------------------------

Parameters can be passed to the notebook in URL query strings by using
:func:`jupyter_invoke.response.get_param`.  For instance,

.. code-block:: python

    from jupyter_invoke import get_param, respond
    key = get_param('key', 'a', optional=False)
    a = {key: [1, 2, 3]}
    respond(a)

Now we would need to invoke the notebook with a query string like
``?key=b`` or otherwise the there will be an error.  In interactive
use the notebook will use the second, default value, parameter for
the variable.  If the ``optional`` flag is set to True, the default
value may also be used in invocation if the parameters isn't provided
in the query.


Error cases
===========

If the requested notebook cannot be found, the HTML status
code will be 404.  In other errors the HTML status code may
be 200 (OK), but the output is a JSON string that contains
the field ``error`` and an explanation.


Limitations
===========

Only Python 3 and notebook versions above 4 are supported.
``python setup.py test`` can be used for testing but it
does not cover the actual integration with a server.

