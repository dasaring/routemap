import pytest
from pathlib import Path
from routemap.parsers import get_parser, detect_parser, available_parsers
from routemap.parsers.grape_parser import GrapeParser


def test_get_parser_grape():
    parser = get_parser('grape')
    assert isinstance(parser, GrapeParser)


def test_get_parser_grape_case_insensitive():
    assert isinstance(get_parser('Grape'), GrapeParser)
    assert isinstance(get_parser('GRAPE'), GrapeParser)


def test_grape_in_available_parsers():
    assert 'grape' in available_parsers()


def test_get_parser_unknown_still_returns_none():
    assert get_parser('unknown_xyz') is None


def test_detect_parser_grape_rb(tmp_path):
    f = tmp_path / 'api.rb'
    f.write_text('class MyAPI < Grape::API\n  get "/ping" do\n  end\nend\n')
    parser = detect_parser(f)
    assert isinstance(parser, GrapeParser)


def test_detect_parser_does_not_match_plain_rb(tmp_path):
    f = tmp_path / 'helper.rb'
    f.write_text('def helper\n  puts "hello"\nend\n')
    parser = detect_parser(f)
    assert not isinstance(parser, GrapeParser)
