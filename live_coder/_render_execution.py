from typing import List, Union

from live_coder._execution_classes import AllFiles, File, ExecutedFunction, LineGroup, Line, FunctionLink


def render_line(line: Union[Line, List[Line]]):
    if type(line) is list:
        line_num = line[0].line_num
        val = ', '.join([f'<span>{lne.value}</span>' for lne in line])
    else:
        line_num, val = line.line_num, f'<span>{line.value}</span>'

    extra_class, extra_data = '', ''
    if hasattr(line, 'call_id'):
        extra_class = ' function_call_link'
        extra_data = f' data-reference-id="{line.call_id}"'

    return f'<div style="height:18px;" class="view-line{extra_class}" data-line_num="{line_num}"{extra_data}>{val}</div>'


def render_line_group(group: LineGroup):
    html_iterations = []
    for group_lines in group.groups:
        html_iterations.append(
            '<div class="iteration">{0}</div>'.format(
                ''.join([
                    render_any_line(line) for line in group_lines
                ])
            )
        )
    return '<div class="loop">{0}</div>'.format(''.join(html_iterations))


def render_any_line(line):
    if type(line) is LineGroup:
        return render_line_group(line)
    return render_line(line)

def render_call(call: ExecutedFunction):
    html = ''
    for line in call.lines:
        html += render_any_line(line)
    return html


def render_file(file: File):
    result = {}
    for name, method in file.methods.items():
        result[name] = {
            'starting_line_number': method.line_num,
            'calls': {call.call_id: render_call(call) for call in method.executions}
        }
    return result


def render_execution(parsed_execution: AllFiles):
    '''
        Convert AllFiles object into dict to send to LiveCoder extension.

        return format:
            {
                'src/main.py': {
                    'test': {
                        'starting_line_number': 4,
                        'calls': {
                            `call id`: `function HTML`,
                            `call id`: `function HTML`
                        }
                    }
                }
            }
    '''
    result = {}
    for path, file in parsed_execution.files.items():
        result[path] = render_file(file)
    return result
