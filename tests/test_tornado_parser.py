import pytest
from pathlib import Path
from routemap.parsers.tornado_parser import TornadoParser

FIXTURE_DIR = Path(__file__).parent / 'fixtures' / 'tornado_app'


@pytest.fixture
def parser():
    return TornadoParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR)


def test_parser_supports_tornado_py(parser, tmp_path):
    f = tmp_path / 'app.py'
    f.write_text('import tornado.web\n')
    assert parser.supports_file(f) is True


def test_parser_supports_from_tornado(parser, tmp_path):
    f = tmp_path / 'handlers.py'
    f.write_text('from tornado import web\n')
    assert parser.supports_file(f) is True


def test_parser_does_not_support_plain_py(parser, tmp_path):
    f = tmp_path / 'utils.py'
    f.write_text('def helper():\n    pass\n')
    assert parser.supports_file(f) is False


def test_parser_does_not_support_js(parser, tmp_path):
    f = tmp_path / 'app.js'
    f.write_text('const express = require("express");\n')
    assert parser.supports_file(f) is False


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_root_path(routes):
    paths = [r.path for r in routes]
    assert '/' in paths


def test_parser_finds_users_path(routes):
    paths = [r.path for r in routes]
    assert '/users' in paths


def test_parser_finds_user_by_id_path(routes):
    paths = [r.path for r in routes]
    assert '/users/([0-9]+)' in paths


def test_parser_finds_get_method(routes):
    methods = [r.method for r in routes]
    assert 'GET' in methods


def test_parser_finds_post_method(routes):
    methods = [r.method for r in routes]
    assert 'POST' in methods


def test_parser_finds_delete_method(routes):
    methods = [r.method for r in routes]
    assert 'DELETE' in methods


def test_route_source_is_set(routes):
    for route in routes:
        assert route.source is not None
        assert route.source.endswith('.py')


def test_parse_empty_dir_returns_empty(parser, tmp_path):
    assert parser.parse(tmp_path) == []
