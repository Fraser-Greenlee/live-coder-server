from fastapi import FastAPI
from pydantic import BaseModel

from live_coder._run_test import run_test
from live_coder._run_discover import run_discover
from live_coder._html_for_snoop_output import html_for_snoop_output


app = FastAPI()


class FindTestsQuery(BaseModel):
    python_path: str
    root_path: str


@app.post("/find_tests")
def find_tests(query: FindTestsQuery):
    '''
        Given a project root path and python path return a list of test classes with methods.
    '''
    return {
        'type': 'testIds',
        'test_ids': run_discover(query.python_path, query.root_path)
    }


class LiveValuesQuery(BaseModel):
    root_path: str
    test_id: str
    python_path: str


def get_calls_id_to_function_map(live_values):
    call_id_to_funciton = {}
    for path in live_values.keys():
        for function_name in live_values[path].keys():
            for call_id, html in live_values[path][function_name]['calls'].items():
                # TODO make call_id
                call_id_to_funciton[call_id] = [path, function_name]
    return call_id_to_funciton


@app.post("/live_values")
def get_live_values(query: LiveValuesQuery):
    '''
        Given a project root path and test id return live values for the test.
    '''
    snoop_output = run_test(query.python_path, query.root_path, query.test_id)
    if snoop_output:
        live_values = html_for_snoop_output(snoop_output)
    else:
        live_values = ''

    return {
        'type': 'liveValues',
        'live_values': live_values,
        'call_id_to_function': get_calls_id_to_function_map(live_values),
        'test_ids': run_discover(query.python_path, query.root_path)
    }
