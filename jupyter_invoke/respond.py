"""Wrappers for Jupyter cell output for parsing the invocation output

The wrappers provide different forms for the output so that
they are displayed nicely in a notebook in a browser and so
that the invocation finds the right piece of data.

Much of the wrapper functionality concerns Pandas DataFrames.  If not
working with Pandas DataFrames, JSON output is works with
``dict`` too.

Use :func:`respond` to wrap the cell output for invocation.

"""
from IPython.display import JSON
import json

try:
    import pandas as pd
except ImportError:
    pd = None

INVOKE_TAG = 'invoke_output'

CSV_OUTPUT = 'text/csv'
JSON_OUTPUT = 'application/json'


def _is_dataframe(x):
    return pd and isinstance(x, pd.DataFrame)


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

    >>> a = {'a': [1, 2], 'b': [3, 4]}
    >>> respond(a, JSON_OUTPUT)
    {'a': [1, 2], 'b': [3, 4]}

    Now the notebook cell output is marked as the output
    for the invocation and this is provided as JSON.

    """
    if mimetype == JSON_OUTPUT:
        return RespondJSON(output, **kwargs)
    elif mimetype == CSV_OUTPUT:
        return RespondCSV(output, **kwargs)
    else:
        raise ValueError('Unknown output type {}, use "{}" or "{}".'
                         ''.format(mimetype, JSON_OUTPUT, CSV_OUTPUT))
