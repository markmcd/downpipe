#!/usr/bin/env python
from google import genai

client = genai.Client()
response = client.models.generate_content_stream(
    model="gemini-3.1-flash-lite-preview",
    contents="Generate a fake annual report about a place called MarkTown. "
             "Use lots of markdown formatting."
)
for chunk in response:
    print(chunk.text, end='', flush=True)
