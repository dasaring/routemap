import pytest
from pathlib import Path
from routemap.parsers import get_parser, detect_parser, available_parsers


def test_get_parser_sinatra():
    parser = get_parser("sinatra")
    assert parser is not None
    assert parser.name == "sinatra"


def test_get_parser_sinatra_case_insensitive():
    assert get_parser("Sinatra") is not None
    assert get_parser("SINATRA") is not None


def test_sinatra_in_available_parsers():
    names = [p.name for p in available_parsers()]
    assert "sinatra" in names


def test_detect_parser_sinatra_file(tmp_path):
    f = tmp_path / "app.rb"
    f.write_text("require 'sinatra'\nget '/ping' do\n  'pong'\nend\n")
    parser = detect_parser(f)
    assert parser is not None
    assert parser.name == "sinatra"


def test_detect_parser_does_not_match_plain_rb(tmp_path):
    f = tmp_path / "plain.rb"
    f.write_text("puts 'hello'\n")
    parser = detect_parser(f)
    # Should not detect sinatra for a plain Ruby file
    if parser is not None:
        assert parser.name != "sinatra"
