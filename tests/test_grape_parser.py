import pytest
from pathlib import Path
from routemap.parsers.grape_parser import GrapeParser

FIXTURE_DIR = Path(__file__).parent / 'fixtures' / 'grape_app'


@pytest.fixture
def parser():
    return GrapeParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR / 'api.rb')


def test_parser_supports_grape_rb(parser, tmp_path):
    f = tmp_path / 'api.rb'
    f.write_text('class MyAPI < Grape::API\n  get "/ping" do\n  end\nend\n')
    assert parser.supports_file(f)


def test_parser_does_not_support_plain_rb(parser, tmp_path):
    f = tmp_path / 'helper.rb'
    f.write_text('def helper\n  puts "hello"\nend\n')
    assert not parser.supports_file(f)


def test_parser_does_not_support_js(parser, tmp_path):
    f = tmp_path / 'app.js'
    f.write_text('const express = require("express");\n')
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_methods(routes):
    methods = {r.method for r in routes}
    assert 'GET' in methods
    assert 'POST' in methods
    assert 'PUT' in methods
    assert 'DELETE' in methods


def test_route_paths_start_with_slash(routes):
    for route in routes:
        assert route.path.startswith('/')


def test_health_check_route(routes):
    paths = [r.path for r in routes]
    assert any('health' in p for p in paths)


def test_parser_returns_route_entries_with_source(routes):
    for route in routes:
        assert route.source is not None
        assert 'api.rb' in route.source


def test_parser_parse_directory(parser, tmp_path):
    f = tmp_path / 'my_api.rb'
    f.write_text(
        'class MyAPI < Grape::API\n'
        '  get "/items" do\n'
        '  end\n'
        '  post "/items" do\n'
        '  end\n'
        'end\n'
    )
    routes = parser.parse(tmp_path)
    assert len(routes) == 2
