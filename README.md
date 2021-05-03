# Live Coder Server (WIP)

Live Coder shows how your code runs as you type.

![Demo GIF](https://media.giphy.com/media/gLWZ9M8YkqQJWXVzBh/giphy.gif)

## Features

See the execution of all functions called for given test.

![GIF shows multiple function's execution syncing scrolling and changing files.](https://media.giphy.com/media/h4g1YyGCgGvHCibw5k/giphy.gif)

Pick between function calls and tests.

![GIF shows picking between fucntion calls and tests.](https://media.giphy.com/media/jR4Uz4lYefwa0Ugifs/giphy.gif)

## Install

Installed as part of the [VSCode Extension](https://marketplace.visualstudio.com/items?itemName=fraser.live-coder).

### Setup

1. Install the Server using: `pip install live-coder`
2. Install the [VSCode Extension](https://marketplace.visualstudio.com/items?itemName=fraser.live-coder)
3. [Watch the intro video](https://www.youtube.com/watch?v=LW_fgRFmEGI)
4. Try the [demo project](https://gitlab.com/Fraser-Greenlee/live-coder-demo-project).

## Having Issues?

Please [add an issue](https://gitlab.com/Fraser-Greenlee/live-coding).

If the server isn't starting, you can start it within Python:

```python
from live_coder.server import app
app.run(host='127.0.0.1', port=5000, debug=False)
```

**Note:** The host and port arguments cannot be changed since the editor extension expects the given ones.

## Thanks

Thanks to the [Pioneer](https://pioneer.app) community for the encouragement, it's worth checking out if you love making things!

If your interested in other new coding tools you should check out the [Future of Coding community](https://futureofcoding.org)!
