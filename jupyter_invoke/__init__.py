from traitlets.config import LoggingConfigurable
from traitlets import Unicode
from notebook.utils import url_path_join
from .invoke import InvokeNotebookHandler
from .response import respond, JSON_OUTPUT, CSV_OUTPUT, get_param


class Invoker(LoggingConfigurable):
    """Configuration parameters for the extensions"""
    filename_pattern = Unicode(
        help="""
        Regex for matching the end of notebook name (before ``.ipynb``)
        to allow invocation.  If not specified, all notebooks are allowed
        to be invoked.
        """
    ).tag(config=True)


def _get_config(web_app):
    """Parsing of the configuration parameters"""
    filename_pattern = web_app.settings['config'].get(
        'Invoker', {}).get('filename_pattern') or ""

    return {'filename_pattern': filename_pattern}


def _jupyter_server_extension_paths():
    return [{
        "module": "jupyter_invoke"
    }]


def load_jupyter_server_extension(nb_server_app):
    """Called when the extension is loaded

    Adapted from
    http://jupyter-notebook.readthedocs.io/en/latest/extending/handlers.html

    """
    web_app = nb_server_app.web_app
    filename_pattern = _get_config(web_app)['filename_pattern']
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'],
                                  '/invoke/(?P<notebook_name>.*{}\.ipynb)'
                                  '(?:\?.*)?$'
                                  ''.format(filename_pattern))
    web_app.add_handlers(host_pattern, [(route_pattern,
                                         InvokeNotebookHandler)])
