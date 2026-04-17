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
    
    stream_markdown(input_data)
    
    captured = capsys.readouterr()
    # Rich's Markdown renderer should produce an ANSI link or at least the text
    # In a non-TTY, it might just be the text, but linkify should have processed it.
    assert "https://google.com" in captured.out

def test_stream_markdown_input_stream(capsys):
    input_data = io.StringIO("Explicit stream test")
    stream_markdown(input_data)
    captured = capsys.readouterr()
    assert "Explicit stream test" in captured.out
