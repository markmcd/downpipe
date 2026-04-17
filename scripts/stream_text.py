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

The end.
"""

for char in text:
    sys.stdout.write(char)
    sys.stdout.flush()
    time.sleep(0.05)
