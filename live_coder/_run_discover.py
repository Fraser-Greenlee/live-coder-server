import subprocess


RUN_DISCOVER_TEMPLATE = '''
import unittest

def print_suite(suite):
    if hasattr(suite, '__iter__'):
        for x in suite:
            print_suite(x)
    else:
        print(suite.id())

print_suite(unittest.defaultTestLoader.discover('.'))
'''


def run_discover(python_path, root_path):
    process = subprocess.run([
        python_path, '-c', RUN_DISCOVER_TEMPLATE
    ], cwd=root_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.stdout.decode('utf-8').strip().split('\n')
