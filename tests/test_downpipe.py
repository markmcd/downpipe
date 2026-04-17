import io
import sys
from downpipe import stream_markdown

def test_stream_markdown_simple(monkeypatch, capsys):
    # Mock stdin with some markdown content
    input_data = io.StringIO("# Hello\nWorld\n")
    
    # We need to mock isatty to false to avoid TTY-specific logic
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    
    stream_markdown(input_data)
    
    captured = capsys.readouterr()
    assert "Hello" in captured.out
    assert "World" in captured.out

def test_stream_markdown_linkify(monkeypatch, capsys):
    # Mock stdin with a URL
    input_data = io.StringIO("Check out https://google.com")
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    
    # We force color so that Rich generates the OSC 8 ansi escape sequence
    # instead of stripping it out for non-TTY.
    stream_markdown(input_data, force_color=True)
    
    captured = capsys.readouterr()
    
    # With linkify working and color forced, Rich will generate a hyperlink.
    # The standard sequence for this is \x1b]8;id=xxx;https://google.com\x1b\
    assert "\x1b]8;" in captured.out
    assert "https://google.com" in captured.out

def test_stream_markdown_input_stream(capsys):
    input_data = io.StringIO("Explicit stream test")
    stream_markdown(input_data)
    captured = capsys.readouterr()
    assert "Explicit stream test" in captured.out

def test_stream_markdown_force_color(capsys):
    input_data = io.StringIO("**Bold**")
    # Force color should produce ANSI escape codes even if stdout is not a TTY
    stream_markdown(input_data, force_color=True)
    captured = capsys.readouterr()
    # ANSI escape for bold/color in Rich usually starts with \x1b[
    assert "\x1b[" in captured.out
    assert "Bold" in captured.out
