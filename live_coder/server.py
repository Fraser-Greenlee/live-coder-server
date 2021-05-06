from fastapi import FastAPI
from pydantic import BaseModel

from live_coder._run_test import run_test
from live_coder._find_tests import find_test_classes
from live_coder._html_for_snoop_output import html_for_snoop_output


found_test_file_ids = []
app = FastAPI()


def _update_found_tests(tests):
    global found_test_file_ids
    found_test_file_ids = []
    for test in tests:
        found_test_file_ids.append(
            test['id'][:test['id'].rfind('.')]
        )


def _get_test_classes(root_path, test_path, test_pattern):
    'throws ImportError'
    test_classes = find_test_classes(found_test_file_ids, root_path, test_path, test_pattern)
    tests = [test_class.serialize() for test_class in test_classes]
    _update_found_tests(tests)
    return tests


class FindTestsQuery(BaseModel):
    root_path: str
    test_path: str
    test_pattern: str


@app.post("/find_tests")
def find_tests(query: FindTestsQuery):
    '''
        Given a project root path and tests directory path and return a list of test classes with methods.
    '''
    try:
        return {
            'type': 'testClasses',
            'testClasses': _get_test_classes(query.root_path, query.test_path, query.test_pattern)
        }
    except ImportError as error:
        return {
            'type': 'error',
            'errorType': 'ImportError',
            'message': str(error)
        }


class LiveValuesQuery(BaseModel):
    root_path: str
    test_id: str
    python_path: str
    test_path: str
    test_pattern: str


def _format_test_id(test_id):
    test_class_id = '.'.join(test_id.split('.')[:-1])
    return test_class_id, test_id


def _test_values(python_path, project_root, test_method_id):
    snoop_output, test_output = run_test(python_path, project_root, test_method_id)
    if snoop_output:
        return html_for_snoop_output(snoop_output), test_output
    return '', test_output


def get_calls_id_to_function_map(live_values):
    call_id_to_funciton = {}
    for path in live_values.keys():
        for function_name in live_values[path].keys():
            for call_id, html in live_values[path][function_name]['calls'].items():
                # TODO make call_id
                call_id_to_funciton[call_id] = [path, function_name]
    return call_id_to_funciton


@app.route("/live_values", methods=['POST'])
def get_live_values(query: LiveValuesQuery):
    '''
        Given a project root path and test id return live values for the test.
    '''
    test_class_id, test_method_id = _format_test_id(query.test_id)

    if 'unittest.loader._FailedTest.' in test_class_id:
        return {
            'type': 'error',
            'errorType': 'ExtensionError',
            'message': 'Extension is sending a failed test id.'
        }

    live_values, test_output = _test_values(query.python_path, query.root_path, test_method_id)
    call_id_to_function = get_calls_id_to_function_map(live_values)

    try:
        test_classes = _get_test_classes(query.root_path, query.test_path, query.test_pattern)
    except ImportError as error:
        return {
            'type': 'error',
            'errorType': 'ImportError',
            'message': str(error)
        }

    return {
        'type': 'live_values',
        'live_values': live_values,
        'call_id_to_function': call_id_to_function,
        'test_output': test_output,
        'test_classes': test_classes
    }
