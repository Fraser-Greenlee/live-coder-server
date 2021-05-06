from re import L
from live_coder._execution_classes import AllFiles, File, ExecutedFunction, LineGroup, Line



def render_line(line: Line):
    return f'<div style="height:18px;" data-line_num="{line.line_number}" class="view-line"><span>{line.value}</span></div>'


def render_line_group(group: LineGroup):
    html_iterations = []
    for lines in group.groups:
        html_iterations.append(
            '<div class="iteration">{0}</div>'.format(
                ''.join([
                    render_line(line) for line in lines
                ])
            )
        )
    return '<div class="loop">{0}</div>'.format(''.join(html_iterations))


def render_call(call: ExecutedFunction):
    html = ''
    for line in call.iter_lines():
        if type(line) is Line:
            html += render_line(line)
        elif type(line) is LineGroup:
            html += render_line_group(line)
    return html


def render_file(file: File):
    result = {}
    for name, method in file.methods.items():
        result[name] = {
            'starting_line_number': method.line_number,
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
