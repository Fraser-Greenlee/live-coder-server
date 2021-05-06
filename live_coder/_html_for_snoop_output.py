from live_coder._parse_execution import parse_execution
from live_coder._render_execution import render_execution


def html_for_snoop_output(snoop_output):
    parsed_execution = parse_execution(snoop_output)
    return render_execution(parsed_execution)
