"""Wrappers for Jupyter cell output for parsing the invocation output

The wrappers provide different forms for the output so that
they are displayed nicely in a notebook in a browser and so
that the invocation finds the right piece of data.

Much of the wrapper functionality concerns Pandas DataFrames.  If not
working with Pandas DataFrames, JSON output is works with
``dict`` too.

Use :func:`respond` to wrap the cell output for invocation.

"""
from IPython.display import display, JSON, Javascript
import json

try:
    import pandas as pd
except ImportError:
    pd = None

INVOKE_TAG = 'invoke_output'

CSV_OUTPUT = 'text/csv'
JSON_OUTPUT = 'application/json'

# This may be assigned to use query parameters with get_param function
QUERY_PARAMETERS = None


def _is_dataframe(x):
    return pd and isinstance(x, pd.DataFrame)


def get_param(name, default, optional=False):
    """Pass query parameters in notebook invocation
    
    This function can be used to use HTTP query parameters
    in an invoked notebook.  In interactive use this uses the
    given default value.
    
    From query parameters this always takes the first occurrence
    of the corresponding parameter and returns it as a string.
    
    By default, this ignores the default value when used in
    invocation and raises an exception if the parameters is not
    provided in the query.
    
    """
    if QUERY_PARAMETERS is None:
        return default
    if name in QUERY_PARAMETERS:
        return QUERY_PARAMETERS[name][0].decode()
    elif optional:
        return default
    else:
        raise ValueError('Parameter {} missing from the query string'
                         ''.format(name))


class RespondJSON(JSON):
    def __init__(self, x, **kwargs):
        super(RespondJSON, self).__init__(x)
        self.json_params = kwargs

    def _check_data(self):
        if _is_dataframe(self.data):
            return
        super(RespondJSON, self)._check_data()

    def _repr_html_(self):
        if _is_dataframe(self.data):
            return self._data.to_html()

    def _repr_json_(self):
        """Dict and metadata dict"""
        if _is_dataframe(self.data):
            return (json.loads(self.data.to_json(**self.json_params)),
                    {INVOKE_TAG: JSON_OUTPUT})
        return self.data, {INVOKE_TAG: JSON_OUTPUT}

    def __repr__(self):
        return repr(self.data)


class RespondCSV(RespondJSON):
    """Wrap the CSV output inside the JSON field

    The CSV is put into the JSON field and in the notebook
    execution phase it is extracted from it.  This work-around
    was made because IPython did not have built-in support for CSV.

    """
    def __init__(self, x, **kwargs):
        super(RespondCSV, self).__init__(x)
        self.csv_params = kwargs

    def _check_data(self):
        if not _is_dataframe(self.data):
            raise ValueError('Can make CSV output only from Pandas DataFrames')

    def _repr_json_(self):
        """Dict and metadata dict"""
        return ({CSV_OUTPUT: self.data.to_csv(**self.csv_params)},
                {INVOKE_TAG: JSON_OUTPUT})


def respond(output, mimetype=JSON_OUTPUT, **kwargs):
    """Wrap Jupyter cell output for invocation

    ``mimetype`` should be "application/json" or "text/csv".
    However, the latter is only supported with Pandas DataFrames.

    ``kwargs`` are passed to Pandas DataFrame ``to_json``
    or ``to_csv`` method if ``output`` is a DataFrame.

    Examples:

    At the end of the notebook cell, call ``respond``:

    >>> a = {'a': [1, 2, 3]}
    >>> respond(a, JSON_OUTPUT)
    <IPython.core.display.Javascript object>
    The following output will be provided as JSON in invocation:
    {'a': [1, 2, 3]}
    >>> import pandas as pd
    >>> b = pd.DataFrame(a)
    >>> b['b'] = [4, 5, 6]
    >>> respond(b, CSV_OUTPUT)
    <IPython.core.display.Javascript object>
    The following output will be provided as CSV in invocation:
       a  b
    0  1  4
    1  2  5
    2  3  6

    In the above example the JavaScript object means that the
    notebook displays the URL for the invocation.

    Now the notebook cell output is marked as the output
    for the invocation from the URL of the notebook where
    ``/notebooks/`` is replaced with ``/invoke/``. 

    """
    output_type = mimetype.split('/')[-1].upper()
    _js_invoke_path(output_type)
    print('The following output will be provided as {} in invocation:'
          ''.format(output_type))
    if mimetype == JSON_OUTPUT:
        return RespondJSON(output, **kwargs)
    elif mimetype == CSV_OUTPUT:
        return RespondCSV(output, **kwargs)
    else:
        raise ValueError('Unknown output type {}, use "{}" or "{}".'
                         ''.format(mimetype, JSON_OUTPUT, CSV_OUTPUT))


def _js_invoke_path(output_type):
    """Display the invoke address in Jupyter"""
    display(Javascript("""
        var address = window.location.href.replace('/notebooks/', '/invoke/');
        alert('{} available at ' + address + ' after saving the notebook ' +
              '(the notebook server may impose limitations regarding ' +
              'acceptable notebook file names).');
        """.format(output_type)))
