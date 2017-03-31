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

In a Jupyter notebook, call function ``respond`` at the end
of one cell to mark it as providing the invocation output:

.. code-block:: python

    from jupyter_invoke import respond
    a = {'a': [1, 2, 3]}
    respond(a)

This will mark the cell as providing JSON output when querying
``http://<server_address>:<port>/invoke/<path/to/notebook.ipynb>``


Error cases
===========

If the requested notebook cannot be found, the HTML status
code will be 404.  In other errors the HTML status code may
be 200 (OK), but the output is a JSON string that contains
the field ``error`` and an explanation.


Limitations
===========

Only Python 3 and notebook version 4 are supported.  Jupyter
version may also affect the functionality.  Running the tests
with ``python setup.py test`` cover some functionality but
not the actual integration with a server.
