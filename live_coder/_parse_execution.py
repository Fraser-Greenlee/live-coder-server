from icecream import ic
from typing import Dict
import re

from live_coder._execution_classes import AllFiles, File, Function, LineGroup, Line, FunctionLink, ExecutedFunction
from live_coder._utils import Stack


def is_snoop_line(line: str):
    return re.search(r'[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9] ', line) is not None


def is_call_line(line: str):
    return line[len('08:35:31.21 '):len('08:35:31.21 >>> Call to ')] == '>>> Call to '


def is_return_line(line: str):
    return line[len('08:35:31.21 '):len('08:35:31.21 <<< Return value from')] == '<<< Return value from'


def is_state_line(line: str):
    dots = line.split()[1]
    return dots == '.' * len(dots)


def get_line_num(line: str):
    tokens = line.split()
    if tokens[2] != '|':
        return None
    try:
        return int(tokens[1])
    except ValueError:
        return None


def parse_return(lines, i):
    line_num = get_line_num(lines[i-1])
    line = lines[i]
    return_value = line[len('08:35:31.67 <<< Return value from ') + len(line.split()[5]) + 1:]
    value = 'return ' + return_value
    return line_num, value


def is_group_line(line):
    tkns = line.split()
    return len(tkns) > 4 and tkns[3] in ['for', 'while']


def get_tab(line):
    past_vert = line[line.find('|')+1:]
    return len(past_vert) - len(past_vert.lstrip())


def is_code_line(line: str):
    return get_line_num(line) is not None


def find_prev_line_num(lines, i):
    line_num = None
    c = i-1
    while not line_num and c > -1:
        line = lines[c]
        if is_call_line(line):
            line_num = int(line.split()[-1])
        else:
            line_num = get_line_num(line)
        c -= 1
    return line_num


def parse_state(lines, i):
    line_num = find_prev_line_num(lines, i)

    if not line_num:
        return None, None

    value = re.sub('[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9] \.* ', '', lines[i])
    return line_num, value


def parse_method(line):
    tkns = line.split()
    method_name, line_num = tkns[4], int(tkns[-1])
    path = line.split()[7][1:-2]
    return path, method_name, line_num


def parse_execution(snoop_output: str):
    all_files = AllFiles()
    method_execs = Stack()

    lines = [l.strip() for l in snoop_output.split('\n')]
    for i, line in enumerate(lines):
        if not is_snoop_line(line):
            continue

        if is_call_line(line):
            path, method_name, line_num = parse_method(line)
            if line_num is None:
                raise Exception(f'Missing line number for method `{line}`.')

            file = all_files.get_file(path)
            method = file.get_method(method_name, line_num)
            a_method_exec = method.get_exec()

            if method_execs.values:
                line_num = find_prev_line_num(lines, i)
                method_execs.peak().add_line(line_num, method_name, call_id=a_method_exec.call_id)
            method_execs.add(a_method_exec)

        elif is_state_line(line):
            line_num, value = parse_state(lines, i)
            if line_num is None:
                raise Exception(f'Missing line number for state `{line}`.')
            method_execs.peak().add_line(line_num, value)

        elif is_code_line(line):
            line_num = get_line_num(line)
            tab = get_tab(line)
            method_execs.peak().handle_group(line_num, tab, is_group_line(line))

        elif is_return_line(line):
            line_num, value = parse_return(lines, i)
            if len(method_execs) >= 2:
                method_execs.peak().add_line(line_num, value, call_id=method_execs.values[-2].call_id, is_return=True)
            method_execs.pop()

    return all_files
