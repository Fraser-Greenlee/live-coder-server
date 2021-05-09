'''
    Runs whole project for Live Coder.
'''
import os
import unittest
from fastapi.testclient import TestClient

from live_coder.server import app
client = TestClient(app)


TEST_ABS_PATH = os.path.abspath('demo_projects/basic-python/tests/test_main.py')
MAIN_ABS_PATH = os.path.abspath('demo_projects/basic-python/basic/main.py')


class TestDiscovery(unittest.TestCase):

    def test_basic(self):
        result = client.post(
            '/find_tests',
            json={
                'root_path': 'demo_projects/basic-python/',
                'python_path': 'venv/bin/python',
            }
        )
        self.assertEqual(result.status_code, 200)
        json_data = result.json()
        self.assertEqual(
            json_data,
            {
                'test_ids': [
                    'tests.test_main.MyTestCase.test_calls',
                    'tests.test_main.MyTestCase.test_fizzbuzz',
                    'tests.test_main.MyTestCase.test_loops',
                    'tests.test_main.MyTestCase.test_ops'
                ],
                'type': 'testIds'
            }
        )


class TestLiveValues(unittest.TestCase):

    def test_basic_fizzbuzz(self):
        result = client.post(
            '/live_values',
            json={
                'root_path': 'demo_projects/basic-python/',
                'test_id': 'tests.test_main.MyTestCase.test_fizzbuzz',
                'python_path': 'venv/bin/python',
            }
        )
        self.assertEqual(result.status_code, 200)
        json_data = result.json()

        call_id_to_func = json_data['call_id_to_function']

        self.assertEqual(
            call_id_to_func[f'{TEST_ABS_PATH}:MyTestCase.test_fizzbuzz:0'],
            [
                TEST_ABS_PATH,
                'MyTestCase.test_fizzbuzz'
            ]
        )
        del call_id_to_func[f'{TEST_ABS_PATH}:MyTestCase.test_fizzbuzz:0']

        self.assertEqual(
            call_id_to_func[f'{MAIN_ABS_PATH}:fizzbuzz:0'],
            [
                MAIN_ABS_PATH,
                'fizzbuzz'
            ]
        )
        del call_id_to_func[f'{MAIN_ABS_PATH}:fizzbuzz:0']

        self.assertEqual(json_data['live_values'][MAIN_ABS_PATH]['fizzbuzz']['starting_line_number'], 2)


    def test_basic_ops(self):
        self.maxDiff = None
        result = client.post(
            '/live_values',
            json={
                'root_path': 'demo_projects/basic-python/',
                'test_id': 'tests.test_main.MyTestCase.test_ops',
                'python_path': 'venv/bin/python',
            }
        )
        self.assertEqual(result.status_code, 200)
        json_data = result.json()
        html = json_data['live_values'][MAIN_ABS_PATH]['ops']['calls'][f'{MAIN_ABS_PATH}:ops:0']
        self.assertEqual(
            html.replace('</div>', '</div>\n'),
            f'''
            <div style="height:18px;" class="view-line" data-line_num="0">
                <span>a = 100</span>, <span>b = 10</span>
            </div>
            <div style="height:18px;" class="view-line" data-line_num="1">
                <span>s = 110</span>
            </div>
            <div style="height:18px;" class="view-line" data-line_num="2">
                <span>s = 11</span><
            /div>
            <div style="height:18px;" class="view-line" data-line_num="3">
                <span>s = \'...........\'</span>
            </div>
            <div style="height:18px;" class="view-line" data-line_num="4">
                <span>s = 11</span>
            </div>
            <div style="height:18px;" class="view-line function_call_link" data-line_num="5" data-reference-id="{TEST_ABS_PATH}:MyTestCase.test_ops:0">
                <span>return 90</span>
            </div>
            '''.strip().replace('    ', '').replace('\n', '').replace('</div>', '</div>\n')
        )


    def test_basic_loops(self):
        result = client.post(
            '/live_values',
            json={
                'root_path': 'demo_projects/basic-python/',
                'test_id': 'tests.test_main.MyTestCase.test_loops',
                'python_path': 'venv/bin/python',
            }
        )
        self.assertEqual(result.status_code, 200)
        json_data = result.json()
        html = json_data['live_values'][MAIN_ABS_PATH]['loops']['calls'][f'{MAIN_ABS_PATH}:loops:0']
        self.assertEqual(
            html.replace('</div>', '</div>\n'),
            f'''
                <div class="loop"><div class="iteration"><div style="height:18px;" class="view-line" data-line_num="2"><span>x = 0</span></div>
                </div>
                <div class="iteration"><div style="height:18px;" class="view-line" data-line_num="2"><span>x = 1</span></div>
                </div>
                <div class="iteration"><div style="height:18px;" class="view-line" data-line_num="2"><span>x = 2</span></div>
                </div>
                <div class="iteration"></div>
                </div>
                <div class="loop"><div class="iteration"><div style="height:18px;" class="view-line" data-line_num="3"><span>y = 0</span></div>
                <div style="height:18px;" class="view-line" data-line_num="4"><span>s = 1</span></div>
                </div>
                <div class="iteration"><div style="height:18px;" class="view-line" data-line_num="3"><span>y = 1</span></div>
                <div style="height:18px;" class="view-line" data-line_num="4"><span>s = 2</span></div>
                </div>
                <div class="iteration"><div style="height:18px;" class="view-line" data-line_num="3"><span>y = 2</span></div>
                <div style="height:18px;" class="view-line" data-line_num="4"><span>s = 3</span></div>
                </div>
                <div class="iteration"></div>
                </div>
                <div class="loop"><div class="iteration"><div style="height:18px;" class="view-line" data-line_num="3"><span>y = 0</span></div>
                <div style="height:18px;" class="view-line" data-line_num="4"><span>s = 4</span></div>
                </div>
                <div class="iteration"><div style="height:18px;" class="view-line" data-line_num="3"><span>y = 1</span></div>
                <div style="height:18px;" class="view-line" data-line_num="4"><span>s = 5</span></div>
                </div>
                <div class="iteration"><div style="height:18px;" class="view-line" data-line_num="3"><span>y = 2</span></div>
                <div style="height:18px;" class="view-line" data-line_num="4"><span>s = 6</span></div>
                </div>
                <div class="iteration"></div>
                </div>
                <div class="loop"><div class="iteration"><div style="height:18px;" class="view-line" data-line_num="3"><span>y = 0</span></div>
                <div style="height:18px;" class="view-line" data-line_num="4"><span>s = 7</span></div>
                </div>
                <div class="iteration"><div style="height:18px;" class="view-line" data-line_num="3"><span>y = 1</span></div>
                <div style="height:18px;" class="view-line" data-line_num="4"><span>s = 8</span></div>
                </div>
                <div class="iteration"><div style="height:18px;" class="view-line" data-line_num="3"><span>y = 2</span></div>
                <div style="height:18px;" class="view-line" data-line_num="4"><span>s = 9</span></div>
                </div>
                <div class="iteration"></div>
                </div>
                <div style="height:18px;" class="view-line function_call_link" data-line_num="5" data-reference-id="{TEST_ABS_PATH}:MyTestCase.test_loops:0"><span>return 9</span></div>
            '''.strip().replace('    ', '').replace('\n', '').replace('</div>', '</div>\n')
        )


    def test_basic_calls(self):
        result = client.post(
            '/live_values',
            json={
                'root_path': 'demo_projects/basic-python/',
                'test_id': 'tests.test_main.MyTestCase.test_calls',
                'python_path': 'venv/bin/python',
            }
        )
        self.assertEqual(result.status_code, 200)
        json_data = result.json()
        calls = list(json_data['live_values'][MAIN_ABS_PATH]['calls']['calls'].keys())
        sorted(calls)
        self.assertEqual(
            calls,
            [
                f'{MAIN_ABS_PATH}:calls:0',
                f'{MAIN_ABS_PATH}:calls:1',
                f'{MAIN_ABS_PATH}:calls:2',
                f'{MAIN_ABS_PATH}:calls:3',
                f'{MAIN_ABS_PATH}:calls:4',
            ]
        )

