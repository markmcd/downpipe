#!/usr/bin/env python
from google import genai

import sys

client = genai.Client()
response = client.models.generate_content_stream(
    model="gemini-3.1-flash-lite-preview",
    contents="Generate a fake annual report about a place called MarkTown. "
             "Use lots of markdown formatting."
)
try:
    for chunk in response:
        print(chunk.text, end='', flush=True)
except BrokenPipeError:
    import os
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stdout.fileno())
    sys.exit(141)
