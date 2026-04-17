import io
import sys
from downpipe import stream_markdown

def test_stream_markdown_simple(monkeypatch, capsys):
    # Mock stdin with some markdown content
    input_data = io.StringIO("# Hello\nWorld\n")
    
    # We need to mock isatty to false to avoid TTY-specific logic
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    
    # Disable color for simple text matching
    stream_markdown(input_data, color=False)
    
    captured = capsys.readouterr()
    assert "Hello" in captured.out
    assert "World" in captured.out

def test_stream_markdown_linkify(monkeypatch, capsys):
    # Mock stdin with a URL
    input_data = io.StringIO("Check out https://google.com")
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    
    # Color is on by default, so Rich will generate a hyperlink.
    stream_markdown(input_data, color=True)
    
    captured = capsys.readouterr()
    
    # The standard sequence for this is \x1b]8;id=xxx;https://google.com\x1b\
    assert "\x1b]8;" in captured.out
    assert "https://google.com" in captured.out

def test_stream_markdown_input_stream(capsys):
    input_data = io.StringIO("Explicit stream test")
    # Disable color for simplicity
    stream_markdown(input_data, color=False)
    captured = capsys.readouterr()
    assert "Explicit stream test" in captured.out

def test_stream_markdown_color_default(capsys):
    input_data = io.StringIO("**Bold**")
    # Color should be on by default
    stream_markdown(input_data)
    captured = capsys.readouterr()
    # ANSI escape for bold/color in Rich usually starts with \x1b[
    assert "\x1b[" in captured.out
    assert "Bold" in captured.out

def test_stream_markdown_indentation_bug(monkeypatch, capsys):
    # Test for the bug where indented code blocks at the start of a "delta" 
    # were improperly stripped or parsed.
    markdown = "# Heading\n\n```python\n    print('indented')\n```\n"
    input_data = io.StringIO(markdown)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    
    stream_markdown(input_data, color=False)
    captured = capsys.readouterr()
    
    # With delta-rendering, the original spacing should be preserved.
    assert "    print('indented')" in captured.out
