from notebook.utils import url_path_join
from .invoke import InvokeNotebookHandler


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
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'],
                                  '/invoke/(.+)$')
    web_app.add_handlers(host_pattern, [(route_pattern,
                                         InvokeNotebookHandler)])
