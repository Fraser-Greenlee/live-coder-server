from fastapi import FastAPI
from pydantic import BaseModel

from live_coder._find_tests import find_test_classes


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
    # TODO validate paths
    # check root_path[-1] == '/'
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
