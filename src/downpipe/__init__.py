"""
downpipe - A Unix-friendly streaming Markdown renderer.

The incremental markdown block detection algorithm used in this script 
was adapted from the Textual framework.

---
Portions of this software are derived from Textual:
Copyright (c) 2021 Will McGugan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
---
"""

import sys
import os
import argparse
from importlib.metadata import version, PackageNotFoundError
from markdown_it import MarkdownIt
from rich.console import Console
from rich.markdown import Markdown

_MARKDOWN_PARSER = MarkdownIt("gfm-like", {"linkify": True}).enable(["linkify", "strikethrough", "table"])

class DownpipeMarkdown(Markdown):
    def __init__(self, markup: str, **kwargs):
        super().__init__(markup, **kwargs)
        # Use our shared parser with linkify enabled
        self.parsed = _MARKDOWN_PARSER.parse(markup)

def stream_markdown(input_stream=sys.stdin, color=True):
    is_tty = sys.stdout.isatty()
    # We use a fixed width if possible to ensure stable rendering.
    # Rich defaults to 80 if it cannot detect terminal width.
    console = Console(force_terminal=color, width=None)
    
    source = ""
    last_stable_source_line_count = 0
    stable_render_lines = []
    partial_height = 0

    def get_render_lines(text):
        if not text.strip():
            return []
        with console.capture() as capture:
            console.print(DownpipeMarkdown(text))
        return capture.get().splitlines()

    try:
        while True:
            char = input_stream.read(1)
            if not char:
                break
            source += char
            
            # Stable block detection
            tokens = _MARKDOWN_PARSER.parse(source)
            top_level_tokens = [t for t in tokens if t.level == 0 and t.map is not None]
            
            stable_source_line_count = 0
            if len(top_level_tokens) > 1:
                # Every block except the last one is stable.
                stable_source_line_count = top_level_tokens[-1].map[0]
            
            # If stable source has grown, flush it
            if stable_source_line_count > last_stable_source_line_count:
                # Clear any partial render before printing stable delta
                if is_tty and partial_height > 0:
                    sys.stdout.write(f"\x1b[{partial_height}A\x1b[J")
                    partial_height = 0
                
                source_lines = source.splitlines(keepends=True)
                stable_source = "".join(source_lines[:stable_source_line_count])
                
                current_stable_render = get_render_lines(stable_source)
                
                # Output the delta of the stable render
                delta = current_stable_render[len(stable_render_lines):]
                if delta:
                    for line in delta:
                        sys.stdout.write(line + "\n")
                    sys.stdout.flush()
                
                stable_render_lines = current_stable_render
                last_stable_source_line_count = stable_source_line_count

            # LIVE PREVIEW (TTY only)
            if is_tty:
                # Render the whole document to get the correct partial lines
                full_render = get_render_lines(source)
                
                # The partial lines are those after the current stable ones
                partial_lines = full_render[len(stable_render_lines):]
                
                if partial_height > 0:
                    sys.stdout.write(f"\x1b[{partial_height}A\x1b[J")
                
                if partial_lines:
                    # Remove trailing empty lines from partial for better feel
                    while partial_lines and not partial_lines[-1].strip():
                        partial_lines.pop()
                    
                    if partial_lines:
                        output = "\n".join(partial_lines) + "\n"
                        sys.stdout.write(output)
                        sys.stdout.flush()
                        partial_height = output.count("\n")
                    else:
                        partial_height = 0
                else:
                    partial_height = 0

    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        # Prevent "Exception ignored" during Python's shutdown flush
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(141) # standard exit code for SIGPIPE
    finally:
        # Final flush of everything remaining.
        try:
            if is_tty and partial_height > 0:
                sys.stdout.write(f"\x1b[{partial_height}A\x1b[J")
            
            full_render = get_render_lines(source)
            delta = full_render[len(stable_render_lines):]
            if delta:
                for line in delta:
                    sys.stdout.write(line + "\n")
                sys.stdout.flush()
        except BrokenPipeError:
            pass

def main():
    try:
        __version__ = version("downpipe")
    except PackageNotFoundError:
        __version__ = "unknown"

    parser = argparse.ArgumentParser(description="A Unix-friendly streaming Markdown renderer")
    parser.add_argument("file", nargs="?", help="Markdown file to render (default: stdin)")
    parser.add_argument("-r", "--raw", action="store_false", dest="color", default=True, help="Disable color output (raw mode)")
    parser.add_argument("--version", action="version", version=f"downpipe {__version__}")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r") as f:
                stream_markdown(f, color=args.color)
        except FileNotFoundError:
            print(f"Error: file '{args.file}' not found", file=sys.stderr)
            sys.exit(1)
    else:
        stream_markdown(sys.stdin, color=args.color)

if __name__ == "__main__":
    main()
