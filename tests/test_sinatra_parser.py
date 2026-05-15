import pytest
from pathlib import Path
from routemap.parsers.sinatra_parser import SinatraParser

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "sinatra_app"


@pytest.fixture
def parser():
    return SinatraParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURES_DIR)


def test_parser_supports_sinatra_rb(parser, tmp_path):
    f = tmp_path / "app.rb"
    f.write_text("require 'sinatra'\nget '/ping' do\n  'pong'\nend\n")
    assert parser.supports_file(f)


def test_parser_supports_sinatra_base(parser, tmp_path):
    f = tmp_path / "api.rb"
    f.write_text("class MyApp < Sinatra::Base\n  get '/hi' do\n    'hello'\n  end\nend\n")
    assert parser.supports_file(f)


def test_parser_does_not_support_plain_rb(parser, tmp_path):
    f = tmp_path / "plain.rb"
    f.write_text("puts 'hello world'\n")
    assert not parser.supports_file(f)


def test_parser_does_not_support_js(parser, tmp_path):
    f = tmp_path / "app.js"
    f.write_text("require('express')\n")
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "PATCH" in methods
    assert "DELETE" in methods


def test_parser_finds_correct_paths(routes):
    paths = {r.path for r in routes}
    assert "/users" in paths
    assert "/users/:id" in paths
    assert "/health" in paths


def test_route_source_is_set(routes):
    for route in routes:
        assert route.source
        assert route.source.endswith(".rb")


def test_parser_name():
    assert SinatraParser.name == "sinatra"
