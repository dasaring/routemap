import pytest
from pathlib import Path
from routemap.parsers import get_parser, detect_parser, available_parsers


def test_get_parser_sanic():
    parser = get_parser("sanic")
    assert parser is not None
    assert parser.__class__.__name__ == "SanicParser"


def test_get_parser_sanic_case_insensitive():
    assert get_parser("Sanic") is not None
    assert get_parser("SANIC") is not None


def test_sanic_in_available_parsers():
    names = [name.lower() for name in available_parsers()]
    assert "sanic" in names


def test_detect_parser_sanic_file(tmp_path):
    f = tmp_path / "app.py"
    f.write_text("from sanic import Sanic\napp = Sanic('test')\n")
    parser = detect_parser(f)
    assert parser is not None
    assert parser.__class__.__name__ == "SanicParser"


def test_detect_parser_does_not_match_plain_py(tmp_path):
    f = tmp_path / "utils.py"
    f.write_text("def helper():\n    return 42\n")
    parser = detect_parser(f)
    # Should not detect as SanicParser
    if parser is not None:
        assert parser.__class__.__name__ != "SanicParser"
