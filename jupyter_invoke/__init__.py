import os
from notebook.utils import url_path_join
from .invoke import InvokeNotebookHandler
from .response import respond, JSON_OUTPUT, CSV_OUTPUT


def _jupyter_server_extension_paths():
    return [{
        "module": "jupyter_invoke"
    }]


def get_extension_parameters():
    """Additional parameters for the extension with environment variables
    
    Parameters:
        
        - INVOKE_FILENAME_PATTERN: regex for matching the end of notebook
          name (before ``.ipynb``) to allow invocation.  If not specified,
          all notebooks are allowed to be invoked.
    
    """
    nb_name_ptrn = os.environ.get('INVOKE_FILENAME_PATTERN', '.+\.ipynb')
    if not nb_name_ptrn.endswith('\.ipynb'):
        nb_name_ptrn += '\.ipynb'
    return {'nb_name_ptrn': nb_name_ptrn}


def load_jupyter_server_extension(nb_server_app):
    """Called when the extension is loaded

    Adapted from
    http://jupyter-notebook.readthedocs.io/en/latest/extending/handlers.html

    """
    params = get_extension_parameters()
    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'],
                                  '/invoke/(.+{})$'
                                  ''.format(params['nb_name_ptrn']))
    web_app.add_handlers(host_pattern, [(route_pattern,
                                         InvokeNotebookHandler)])
