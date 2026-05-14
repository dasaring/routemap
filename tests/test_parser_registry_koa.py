import pytest
from pathlib import Path
from routemap.parsers import get_parser, detect_parser, available_parsers


def test_get_parser_koa():
    parser = get_parser("koa")
    assert parser is not None
    assert type(parser).__name__ == "KoaParser"


def test_get_parser_koa_case_insensitive():
    assert get_parser("Koa") is not None
    assert get_parser("KOA") is not None


def test_koa_in_available_parsers():
    names = [name.lower() for name in available_parsers()]
    assert "koa" in names


def test_detect_parser_koa_js(tmp_path):
    f = tmp_path / "app.js"
    f.write_text("const Router = require('koa-router');\nrouter.get('/x', fn);")
    parser = detect_parser(f)
    assert parser is not None
    assert type(parser).__name__ == "KoaParser"


def test_detect_parser_does_not_match_plain_js(tmp_path):
    f = tmp_path / "plain.js"
    f.write_text("console.log('hello world');")
    parser = detect_parser(f)
    # Should not be KoaParser for plain JS without koa-router
    if parser is not None:
        assert type(parser).__name__ != "KoaParser"
