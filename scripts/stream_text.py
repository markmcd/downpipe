#!/usr/bin/env python
import sys
import time

text = """# This is a test
This is some **bold** text that should stream.
And a list:
- Item 1
- Item 2
- Item 3

```python
print("Hello World")
```

For more info see [bing](https://google.com).

The end.
"""

for char in text:
    try:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.05)
    except BrokenPipeError:
        import os
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(141)
