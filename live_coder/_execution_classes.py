from typing import List, Dict
import json

from live_coder._utils import Stack


class ReprDict:
    def __repr__(self) -> str:
        return json.dumps(self.to_dict(), indent=4)


class AllFiles(ReprDict):
    def __init__(self):
        self.files = {}

    def get_file(self, path: str):
        if path not in self.files:
            self.files[path] = File(path)
        return self.files[path]

    def to_dict(self):
        return {
            'type': 'AllFiles',
            'files': {k: v.to_dict() for k, v in self.files.items()}
        }


class File(ReprDict):
    def __init__(self, path):
        self.path = path
        self.methods = {}

    def get_method(self, name, line_num):
        if name not in self.methods:
            self.methods[name] = Function(self, name, line_num)
        return self.methods[name]

    def to_dict(self):
        return {
            'type': 'File',
            'path': self.path,
            'methods': {k: v.to_dict() for k, v in self.methods.items()},
        }


class Function(ReprDict):
    def __init__(self, file: File, name: str, line_num: int):
        self.file = file
        self.name = name
        self.line_num = line_num
        self.executions = []

    def get_exec(self, i = None):
        if i is None:
            i = len(self.executions)
            self.executions.append(ExecutedFunction(self, i))
        return self.executions[i]

    def to_dict(self):
        return {
            'type': 'Function',
            'name': self.name,
            'line_num': self.line_num,
            'self.executions': [v.to_dict() for v in self.executions],
        }


class Line(ReprDict):
    '''
        Represents a value line (starts with ... in snoops).
    '''
    def __init__(self, line_num: int, value: str):
        self.value = value
        self.line_num = line_num

    def to_dict(self):
        return {
            'type': 'Line',
            'value': self.value,
            'line_num': self.line_num,
        }


class FunctionLink(Line):
    '''
        Gives a link to another function call.
    '''
    def __init__(self, call_id: str, *args):
        super().__init__(*args)
        self.call_id = call_id

    def to_dict(self):
        return {
            'type': 'FunctionLink',
            'value': self.value,
            'line_num': self.line_num,
            'call_id': self.call_id
        }


class LineGroup(ReprDict):
    '''
        Holds lines for one run of a loop.
    '''
    def __init__(self, line_num, tab):
        self.line_num = line_num
        self.tab = tab
        self.groups = [[]] # List[List[Line, LineGroup]]

    def add_line(self, line: Line):
        self.groups[-1].append(line)

    def start_new_group(self):
        self.groups.append([])

    def _get_last_line(self):
        if self.groups and self.groups[-1]:
            return self.groups[-1][-1]
        return None

    def _set_last_line(self, line):
        if self.groups and self.groups[-1]:
            self.groups[-1][-1] = line
        else:
            raise Exception('No line to set.')

    def to_dict(self):
        return {
            'type': 'LineGroup',
            'line_num': self.line_num,
            'tab': self.tab,
            'groups': [line.to_dict() if type(line) is not list else [l.to_dict() for l in line] for line in self.groups]
        }


class ExecutedFunction(ReprDict):
    '''
        Represent the execution of a function.

        .lines = lines outputted
            Each line has a line number & state change.
            A list of lines denotes multiple state changes occuring on the same line.
            A line group denotes lines that are repeated multiple times per execution.
    '''
    def __init__(self, method: Function, nth_call: int):
        self.method = method
        self.nth_call = nth_call
        self.call_id = f'{self.method.file.path}:{self.method.name}:{self.nth_call}'
        self.lines = []
        self.groups = Stack()


    def norm_line_num(self, line_num):
        return line_num - self.method.line_num

    def handle_group(self, line_num, tab, is_group_line):
        '''
            Handles creation/exit of groups.

            Each group has a tab level, once a line of code is seen with the a tab <= it the group is exited.

            Can have recursive loops so groups are kept in a stack.
        '''
        line_num = self.norm_line_num(line_num)

        # exit groups
        while self.groups.peak() and tab < self.groups.peak().tab:
            self.groups.pop()

        if self.groups.peak() and tab == self.groups.peak().tab and line_num != self.groups.peak().line_num:
            self.groups.pop()

        # add a group
        if is_group_line:
            if self.groups.peak() and line_num == self.groups.peak().line_num:
                self.groups.peak().start_new_group()
            else:
                group = LineGroup(line_num, tab)
                self.groups.add(group)
                self.lines.append(group)

    def _get_last_line(self):
        if self.groups.peak():
            return self.groups.peak()._get_last_line()
        if self.lines:
            return self.lines[-1]
        return None

    def _set_last_line(self, line):
        if self.groups.peak():
            self.groups.peak()._set_last_line(line)
        elif self.lines:
            self.lines[-1] = line
        else:
            raise Exception('No last line to set.')

    def _append_line(self, line):
        if self.groups.peak():
            self.groups.peak().add_line(line)
        else:
            self.lines.append(line)

    def _add_line(self, line_num, line):
        last_line = self._get_last_line()

        if last_line:

            if type(last_line) is list:
                last_line_num = last_line[0].line_num
            else:
                last_line_num = last_line.line_num

            if last_line_num == line_num:
                if type(last_line) is list:
                    last_line.append(line)
                else:
                    last_line = [last_line, line]
                try:
                    self._set_last_line(last_line)
                except Exception:
                    import pdb
                    pdb.set_trace()
                return None

        self._append_line(line)

    def add_line(self, line_num, value, call_id=None, is_return=False):
        if line_num:
            line_num = self.norm_line_num(line_num)
        elif is_return is False:
            raise Exception('No line_num for non-return line.')

        if call_id:
            line = FunctionLink(call_id, line_num, value)
        else:
            line = Line(line_num, value)

        self._add_line(line_num, line)

    def to_dict(self):
        return {
            'type': 'ExecutedFunction',
            'nth_call': self.nth_call,
            'call_id': self.call_id,
            'lines': [line.to_dict() if type(line) is not list else [l.to_dict() for l in line] for line in self.lines],
            'groups': self.groups.to_dict()
        }
