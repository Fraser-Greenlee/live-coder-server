from typing import Dict
import re

from live_coder._execution_classes import AllFiles, File, Function, LineGroup, Line, FunctionLink, ExecutedFunction


def is_call_line(line: str):
    return line[len('08:35:31.21 '):len('>>> Call to')] == '>>> Call to'


def is_return_line(line: str):
    return line[len('08:35:31.21 '):len('<<< Return value from')] == '<<< Return value from'


def parse_call(lines, i):
    line = lines[i]
    tokens = line.split()
    return int(tokens[-1]), tokens[4]


def is_state_line(line: str):
    dots = line.split()[1]
    return dots == '.' * len(dots)


def get_line_num(line: str):
    tokens = line.split()
    try:
        line_num = int(tokens[1])
    except ValueError:
        return None
    if tokens[2] != '|':
        return None
    return line_num


def parse_return(lines, i):
    line_num = get_line_num(lines[i-1])
    line = lines[i]
    value = 'return ' + line[len('08:35:31.67 <<< Return value from ') + line.split(5) + 1:]
    return line_num, value


def is_code_line(line: str):
    return get_line_num(line) is None


def parse_state(lines, i):
    line_num = get_line_num(lines[i-1])
    if not line_num:
        line_num = get_line_num(lines[i+1])
        if not line_num:
            return None

    line = lines[i]
    import pdb
    # TODO check this regex sub replace
    pdb.set_trace()
    value = re.sub('[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9] \.* ', '', line.strip())
    return line_num, value


def parse_method(line):
    method_name = line.split()[4]
    path = line.split()[7][1:-2]
    return path, method_name


def parse_execution(snoop_output: str):
    all_files = AllFiles()
    method_exec_stack = []

    lines = snoop_output.split('\n')
    for i, line in enumerate(lines):

        if is_call_line(line):
            path, method_name = parse_method(line)
            file = all_files.get_file(path)
            method = file.get_method(method_name)
            method_exec = method.get_exec()
            if method_exec_stack:
                line_num, value = parse_call(lines, i)
                method_exec_stack[-1].add_line(
                    FunctionLink(line_num, value, method_exec.call_id)
                )
            method_exec_stack.append(method_exec)

        elif is_state_line(line):
            line_num, value = parse_state(lines, i)
            method_exec_stack[-1].add_line(line_num, value)

        elif is_code_line(line):
            start, end = method_exec_stack[-1].is_repeate(line)
            if start:
                method_exec_stack[-1].add_group(start, end)

        elif is_return_line(line):
            line_num, value = parse_return(lines, i)
            if len(method_exec_stack) >= 2:
                method_exec_stack[-1].add_line(
                    FunctionLink(line_num, value, method_exec_stack[-2].call_id)
                )
            method_exec_stack.pop(-1)

    return all_files
