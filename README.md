# downpipe

A Unix-friendly streaming Markdown renderer based on [Rich](https://github.com/textualize/rich) and [Textual](https://github.com/textualize/textual).

`downpipe` (invoked as `dp`) streams Markdown from `stdin` and renders it to `stdout` using [Rich](https://github.com/Textualize/rich).

It is designed to be used in Unix pipelines, providing rich, coloured output as soon as the first token hits. Recommended for use with CLI LLM tools like [`llm`](https://github.com/simonw/llm).

## Features

- **Snappy byte-by-byte streaming**: Feels as fast as your input does.
- **Stable block detection** (from Textual): Only outputs finalized blocks to pipes, preventing intermediate rendering artifacts.
- **Live TTY preview**: Smooth, flicker-free updates in your terminal.
- **Unix-friendly**: Smartly detects TTY vs. pipe to adjust formatting and ANSI escapes.

## Installation

```bash
pip install downpipe
```

## Usage

```bash
# Live rendering of a growing file
tail -f something.md | dp

# Using in a pipeline
cat large_doc.md | dp | grep "Important"
```

## Credits

This entire project is a very thin wrapper around [Will McGugan](https://github.com/willmcgugan)'s work, using Rich for rendering and Textual's block detection algorithm for efficient stable streaming. All the credit goes to Will but if you find bugs they're my fault.

## License

MIT
