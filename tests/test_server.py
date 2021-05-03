'''
    Runs whole project for Live Coder.
'''
import unittest
from fastapi.testclient import TestClient

from live_coder.server import app
client = TestClient(app)


class TestDiscovery(unittest.TestCase):

    def test_basic(self):
        result = client.post(
            '/find_tests',
            json={
                'root_path': 'demo_projects/basic-python/',
                'test_path': 'tests/',
                'test_pattern': 'test_*.py'
            }
        )
        self.assertEqual(result.status_code, 200)
        json_data = result.json()
        self.assertEqual(
            json_data,
            {
                'testClasses': [
                    {
                        'id': 'tests.test_main.MyTestCase',
                        'method_ids': ['tests.test_main.MyTestCase.test_fizzbuzz'],
                        'method_names': ['test_fizzbuzz'],
                        'type': 'TestClass'
                    }
                ],
                'type': 'testClasses'
            }
        )
