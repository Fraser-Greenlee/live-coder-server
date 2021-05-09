import subprocess

RUN_COMMAND_TEMPLATE = '{python_path} -m unittest {folder}{file}.{test_class}.{method}'

def _params_from_test_parts(test_parts):
    filename, test_class, test_method = test_parts[-3:]
    folder = ''
    if len(test_parts) > 3:
        folder = '.'.join(test_parts[:-3]) + '.'
    return folder, filename, test_class, test_method


def run_test(python_path, project_root, test_id):
    '''
        Runs a Python test & returns debug logs for each line.
    '''
    folder, filename, test_class, test_method = _params_from_test_parts(test_id.split('.'))
    run_command = RUN_COMMAND_TEMPLATE.format(
        python_path = python_path,
        folder = folder,
        file = filename,
        test_class = test_class,
        method = test_method
    )
    process = subprocess.run(run_command.split(), cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.stderr.decode('utf-8')
