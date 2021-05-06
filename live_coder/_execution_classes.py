from typing import List, Dict


class AllFiles:
    files = {}

    def get_file(self, path: str):
        if path not in self.files:
            self.files[path] = File(path)
        return self.files[path]


class File:
    methods = {}

    def __init__(self, path):
        self.path = path

    def get_method(self, name):
        if name not in self.methods:
            self.methods[name] = Function(name)
        return self.methods[name]


class Function:
    executions = []

    def __init__(self, file: File, name: str, line_number: int):
        self.file = file
        self.name = name
        self.line_number = line_number

    def get_exec(self, i = None):
        if i is None:
            i = len(self.executions)
            self.executions.append(ExecutedFunction(self, i))
        return self.executions[i]


class Line:
    '''
        Represents a value line (starts with ... in snoops).
    '''
    def __init__(self, line_number: int, value: str):
        self.value = value
        self.line_number = line_number


class LineGroup:
    '''
        Holds lines for one run of a loop.
    '''
    groups: List[List[Line]] = []

    def __init__(self, start_line: int, end_line: int, lines: List[Line]):
        self.start = start_line
        self.end = end_line
        self.groups = [lines, []]

    def add_line(self, line: Line):
        self.groups[-1].append(line)

    def new_group(self):
        self.groups.append([])


class FunctionLink(Line):
    '''
        Gives a link to another function call.
    '''
    def __init__(self, *args, call_id: str):
        super().__init__(*args)
        self.call_id = call_id


class ExecutedFunction:
    '''
        Represent the execution of a function.

        .name = the function name
        .changes = list of change values
    '''
    lines: Dict[int, Line] = {}

    def __init__(self, method: Function, nth_call: int):
        self.method = method
        self.nth_call = nth_call
        self.call_id = self.method.file.path + ':' + self.method.name + ':' + self.nth_call

    def pop_range(self, start, end):
        lines = []
        for line_num in range(start, end):
            if line_num in self.lines:
                assert(type(self.lines[line_num] is Line), 'Overlapping group broke execution.')
                lines.append(self.lines[line_num])
                del self.lines[line_num]
        return lines

    def add_group(self, start: int, end: int):
        if type(self.lines[start]) is LineGroup:
            return self.lines[start].new_group()

        lines = self.pop_range(start, end)
        group = LineGroup(start, end, lines)
        for i in range(group.start, group.end):
            self.lines[i] = group

    def add_line(self, line_number, value):
        line = Line(line_number, value)

        if line_number not in self.lines:
            self.lines[line_number] = line
        else:
            if type(self.lines[line_number]) is LineGroup:
                self.lines[line_number].add_line(line)
            else:
                raise ValueError('Overlapping lines.')

    def iter_lines(self):
        prev_line = None
        for line in self.lines.values():
            if line == prev_line:
                # skip line group duplicates
                continue
            yield line
