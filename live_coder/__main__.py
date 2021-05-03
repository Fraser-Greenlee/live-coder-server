import os
from sys import argv as arguments
from live_coder.server import app


PORT = int(arguments[1])
VENV = arguments[2]

assert os.path.exists(VENV), f'Virtual enviroment path `{VENV}` could not be found.'

app.run(host='127.0.0.1', port=PORT, debug=True)
