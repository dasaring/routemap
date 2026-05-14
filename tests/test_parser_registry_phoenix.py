import pytest
from pathlib import Path
from routemap.parsers import get_parser, detect_parser, available_parsers
from routemap.parsers.phoenix_parser import PhoenixParser


def test_get_parser_phoenix():
    parser = get_parser("phoenix")
    assert isinstance(parser, PhoenixParser)


def test_get_parser_phoenix_case_insensitive():
    assert isinstance(get_parser("Phoenix"), PhoenixParser)
    assert isinstance(get_parser("PHOENIX"), PhoenixParser)


def test_phoenix_in_available_parsers():
    parsers = available_parsers()
    assert "phoenix" in parsers


def test_detect_parser_router_ex(tmp_path):
    f = tmp_path / "router.ex"
    f.write_text('defmodule MyAppWeb.Router do\n  use Phoenix.Router\nend\n')
    parser = detect_parser(f)
    assert isinstance(parser, PhoenixParser)


def test_detect_parser_does_not_match_plain_ex(tmp_path):
    f = tmp_path / "schema.ex"
    f.write_text('defmodule MyApp.Schema do\n  use Ecto.Schema\nend\n')
    parser = detect_parser(f)
    assert not isinstance(parser, PhoenixParser)
