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
import argparse
from importlib.metadata import version, PackageNotFoundError
from markdown_it import MarkdownIt
from rich.console import Console
from rich.markdown import Markdown

def stream_markdown(input_stream=sys.stdin, force_color=False):
    is_tty = sys.stdout.isatty()
    # If it's a TTY, we want to know the width for proper wrapping.
    # If it's a pipe, we want to avoid wrapping or use a fixed width.
    console = Console(force_terminal=is_tty or force_color, width=None)
    md_it = MarkdownIt("gfm-like", {"linkify": True})
    md_it.enable(["linkify"])
    
    source = ""
    last_flushed_line = 0
    partial_height = 0

    try:
        while True:
            char = input_stream.read(1)
            if not char:
                break
            source += char
            
            # We split the source into lines.
            lines = source.splitlines(keepends=True)
            if not lines:
                continue

            # We parse everything since the last flush.
            to_parse = "".join(lines[last_flushed_line:])
            tokens = md_it.parse(to_parse)
            
            # Stable block detection (adapted from Textual)
            # We identify top-level blocks.
            top_level_tokens = [t for t in tokens if t.level == 0 and t.map is not None]
            
            stable_lines = 0
            if len(top_level_tokens) > 1:
                # Every block except the last one is stable.
                # The start of the last block is our stable line limit.
                stable_lines = top_level_tokens[-1].map[0]
            
            # Blank line rule: a block is definitely finished if followed by a blank line.
            # We check if the last line in our current to_parse is a newline followed by empty content
            # or if we have a sequence of two newlines.
            if len(lines) > 1 and lines[-1].strip() == "" and lines[-2].strip() != "":
                stable_lines = len(lines) - last_flushed_line - 1

            # If we found stable content, flush it.
            if stable_lines > 0:
                if is_tty and partial_height > 0:
                    # Move cursor up and clear the old partial render.
                    sys.stdout.write(f"\x1b[{partial_height}A\x1b[J")
                    partial_height = 0
                
                chunk_to_print = "".join(lines[last_flushed_line : last_flushed_line + stable_lines])
                console.print(Markdown(chunk_to_print))
                last_flushed_line += stable_lines
                sys.stdout.flush()

            # LIVE PREVIEW (TTY only)
            if is_tty:
                current_chunk = "".join(lines[last_flushed_line:])
                if current_chunk.strip():
                    if partial_height > 0:
                        sys.stdout.write(f"\x1b[{partial_height}A\x1b[J")
                    
                    with console.capture() as capture:
                        console.print(Markdown(current_chunk))
                    rendered = capture.get()
                    
                    # We want to avoid trailing whitespace/newlines from console.print
                    # so we can track exact line count.
                    rendered_lines = rendered.splitlines()
                    while rendered_lines and not rendered_lines[-1].strip():
                        rendered_lines.pop()
                    
                    if rendered_lines:
                        final_render = "\n".join(rendered_lines) + "\n"
                        sys.stdout.write(final_render)
                        sys.stdout.flush()
                        partial_height = final_render.count("\n")
                    else:
                        partial_height = 0
                elif partial_height > 0:
                    # Current chunk is empty, but we had a partial render. Clear it.
                    sys.stdout.write(f"\x1b[{partial_height}A\x1b[J")
                    partial_height = 0

    except KeyboardInterrupt:
        pass
    finally:
        # Final flush of remaining content.
        if is_tty and partial_height > 0:
            sys.stdout.write(f"\x1b[{partial_height}A\x1b[J")
        
        remaining = "".join(source.splitlines(keepends=True)[last_flushed_line:])
        if remaining.strip():
            console.print(Markdown(remaining))
            sys.stdout.flush()

def main():
    try:
        __version__ = version("downpipe")
    except PackageNotFoundError:
        __version__ = "unknown"

    parser = argparse.ArgumentParser(description="A Unix-friendly streaming Markdown renderer")
    parser.add_argument("file", nargs="?", help="Markdown file to render (default: stdin)")
    parser.add_argument("-C", "--color", action="store_true", help="Force color output even when piping")
    parser.add_argument("--version", action="version", version=f"downpipe {__version__}")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r") as f:
                stream_markdown(f, force_color=args.color)
        except FileNotFoundError:
            print(f"Error: file '{args.file}' not found", file=sys.stderr)
            sys.exit(1)
    else:
        stream_markdown(sys.stdin, force_color=args.color)

if __name__ == "__main__":
    main()
