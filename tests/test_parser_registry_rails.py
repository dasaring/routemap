import pytest
from pathlib import Path
from routemap.parsers import get_parser, detect_parser, available_parsers
from routemap.parsers.rails_parser import RailsParser


def test_get_parser_rails():
    parser = get_parser("rails")
    assert isinstance(parser, RailsParser)


def test_get_parser_rails_case_insensitive():
    assert isinstance(get_parser("Rails"), RailsParser)
    assert isinstance(get_parser("RAILS"), RailsParser)


def test_rails_in_available_parsers():
    parsers = available_parsers()
    assert "rails" in parsers


def test_detect_parser_routes_rb():
    path = Path("config/routes.rb")
    parser = detect_parser(path)
    assert isinstance(parser, RailsParser)


def test_detect_parser_does_not_match_other_rb():
    path = Path("app/models/user.rb")
    parser = detect_parser(path)
    assert not isinstance(parser, RailsParser)
