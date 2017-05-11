import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError
from notebook.base.handlers import IPythonHandler

import os

from .response import CSV_OUTPUT, JSON_OUTPUT, INVOKE_TAG


class InvokeNotebookHandler(IPythonHandler):
    """Execute notebook and return the output"""
    def get(self, notebook_name):
        try:
            query_params = self.request.arguments
            output, mimetype = execute_notebook(notebook_name, query_params)
            output_filename = os.path.basename(notebook_name)
            output_filename = output_filename.replace('.ipynb', '')
            ext = mimetype.split('/')[-1]
            self.set_header('Content-Type', mimetype)
            self.set_header('Content-Disposition',
                            'inline; filename="{}.{}"'
                            ''.format(output_filename, ext))
            self.finish(output)
        except InvokeException as e:
            self.set_status(e.status_code)
            self.write(e.error_dict)


class InvokeException(Exception):
    """Expected error from execution or parsing of output"""
    def __init__(self, msg, results=None, status_code=200, *args, **kwargs):
        super(InvokeException, self).__init__(msg, *args, **kwargs)
        if results is None:
            self.error_dict = {'error': msg}
        else:
            self.error_dict = {'error': msg, 'outputs': results}
        self.status_code = status_code


def handle_query_parameters(notebook, query_parameters):
    """Insert a cell in the beginning of the notebook for query parameters
    
    This modifies the notebook so that :func:`jupyter_invoke.respond.get_param`
    look for keys and values from given HTTP request parameters
    
    """
    first_cell = {'cell_type': 'code',
                  'source': "from jupyter_invoke import response\n"
                             "response.QUERY_PARAMETERS = {!r}"
                             "".format(query_parameters)}
    notebook['cells'].insert(0, nbformat.notebooknode.NotebookNode(first_cell))


def execute_notebook(notebook_name, query_params=None):
    """Execute the notebook from path and parse the output"""
    if not os.path.exists(notebook_name):
        msg = 'Cannot find notebook {}'.format(notebook_name)
        raise InvokeException(msg, status_code=404)
    with open(notebook_name) as f:
        notebook = nbformat.read(f, as_version=4)
    handle_query_parameters(notebook, query_params)
    ep = ExecutePreprocessor(timeout=300, kernel_name='python3')
    try:
        executed_notebook = ep.preprocess(notebook,
                                          {'metadata': {'path': ''}})
    except CellExecutionError as e:
        msg = 'Unable to execute notebook {}\n{}'.format(notebook_name,
                                                         str(e))
        raise InvokeException(msg)

    return parse_execute_output(executed_notebook, notebook_name)


def parse_execute_output(executed_notebook, notebook_name):
    """Parse the output cells for 'invoke_output'

    The output metadata of one cell should define 'invoke_output' key
    (it should be inside "application/json" field). This key indicates
    which field is used for the output dict.

    CSV output is extracted from inside the "application/json" field
    of the output (see the FIXME below).

    The cell output should be created with
    :func:`jupyter_invoke.respond.respond`.

    """
    results = []
    for nb in executed_notebook:
        for cell in nb.get('cells', []):
            for output in cell.get('outputs', []):
                if (output['output_type'] == 'execute_result'
                        and JSON_OUTPUT in output['metadata']
                        and INVOKE_TAG in output['metadata'][JSON_OUTPUT]):
                    output_type = output['metadata'][JSON_OUTPUT][INVOKE_TAG]
                    result = output['data'][output_type]
                    # FIXME: Ugly special case for CSV output
                    if CSV_OUTPUT in result:
                        result = result[CSV_OUTPUT]
                        output_type = CSV_OUTPUT
                    results.append((result, output_type))

    if len(results) == 0:
        msg = ('Cannot find a cell with a proper output metadata tag "{}" '
               'from notebook {}'.format(INVOKE_TAG, notebook_name))
        raise InvokeException(msg)
    elif len(results) > 1:
        msg = ('Multiple cells with output metadata tag "{}" in {}'
               ''.format(INVOKE_TAG, notebook_name))
        raise InvokeException(msg, results)

    return results[0]
