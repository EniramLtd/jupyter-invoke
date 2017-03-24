from jupyter_invoke.invoke import execute_notebook, InvokeException
import pytest
import os

@pytest.mark.parametrize('nb_name,expected,status_code,error_extra',[
    ('notebooks/success_csv.ipynb', (""";a;b
2017-01-01;1;3
2017-01-02;2;4
2017-01-03;3;5\n""", 'text/csv'), None, None),
    ('notebooks/success_json.ipynb',
     ({"a": {"2017-01-01T00:00:00.000Z": 1,
             "2017-01-02T00:00:00.000Z": 2},
       "b": {"2017-01-01T00:00:00.000Z": 3,
             "2017-01-02T00:00:00.000Z": 4}}, 'application/json'), None, None),
    ('notebooks/no_output_cell.ipynb', 'Cannot find a cell', 200, None),
    ('notebooks/many_output_cells.ipynb', 'Multiple cells with', 200,
     [({'a': 1, 'b': 2}, 'application/json'), ({'a': 1}, 'application/json')])
])
def test_notebooks(nb_name, expected, status_code, error_extra):
    os.chdir(os.path.dirname(__file__))
    try:
        result = execute_notebook(nb_name)
        assert result == expected
    except InvokeException as e:
        assert expected in str(e)
        assert e.status_code == status_code
        assert expected in e.error_dict['error']
        if error_extra:
            assert error_extra == e.error_dict['outputs']
