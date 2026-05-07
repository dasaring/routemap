import pytest
from pathlib import Path
from routemap.parsers import get_parser, detect_parser, available_parsers
from routemap.parsers.fastapi_parser import FastAPIParser
from routemap.parsers.express_parser import ExpressParser
from routemap.parsers.django_parser import DjangoParser


def test_get_parser_fastapi():
    assert isinstance(get_parser("fastapi"), FastAPIParser)


def test_get_parser_express():
    assert isinstance(get_parser("express"), ExpressParser)


def test_get_parser_django():
    assert isinstance(get_parser("django"), DjangoParser)


def test_get_parser_case_insensitive():
    assert isinstance(get_parser("FastAPI"), FastAPIParser)
    assert isinstance(get_parser("DJANGO"), DjangoParser)


def test_get_parser_unknown_returns_none():
    assert get_parser("rails") is None


def test_available_parsers_contains_all():
    names = available_parsers()
    assert "fastapi" in names
    assert "express" in names
    assert "django" in names


def test_detect_parser_fastapi(tmp_path):
    (tmp_path / "requirements.txt").write_text("fastapi==0.100.0\nuvicorn\n")
    parser = detect_parser(tmp_path)
    assert isinstance(parser, FastAPIParser)


def test_detect_parser_django(tmp_path):
    (tmp_path / "requirements.txt").write_text("django>=4.0\npsycopg2\n")
    parser = detect_parser(tmp_path)
    assert isinstance(parser, DjangoParser)


def test_detect_parser_express_via_package_json(tmp_path):
    (tmp_path / "package.json").write_text('{"name": "my-app"}')
    parser = detect_parser(tmp_path)
    assert isinstance(parser, ExpressParser)


def test_detect_parser_django_via_manage(tmp_path):
    (tmp_path / "manage.py").write_text("# django manage")
    parser = detect_parser(tmp_path)
    assert isinstance(parser, DjangoParser)


def test_detect_parser_unknown_returns_none(tmp_path):
    parser = detect_parser(tmp_path)
    assert parser is None
