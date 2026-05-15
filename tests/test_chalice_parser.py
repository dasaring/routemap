import textwrap
from pathlib import Path

import pytest

from routemap.parsers.chalice_parser import ChaliceParser


CHALICE_APP_CONTENT = textwrap.dedent("""
    from chalice import Chalice

    app = Chalice(app_name='myapp')

    @app.route('/')
    def index():
        return {'hello': 'world'}

    @app.route('/users', methods=['GET', 'POST'])
    def users():
        return {}

    @app.route('/users/{user_id}', methods=['GET', 'PUT', 'DELETE'])
    def user_detail(user_id):
        return {}

    @app.route('/health')
    def health():
        return {'status': 'ok'}
""")


@pytest.fixture()
def tmp_chalice_file(tmp_path: Path) -> Path:
    f = tmp_path / "app.py"
    f.write_text(CHALICE_APP_CONTENT)
    return f


@pytest.fixture()
def parser() -> ChaliceParser:
    return ChaliceParser()


@pytest.fixture()
def routes(parser: ChaliceParser, tmp_chalice_file: Path):
    return parser.parse(tmp_chalice_file)


def test_parser_supports_chalice_py(parser: ChaliceParser, tmp_chalice_file: Path):
    assert parser.supports_file(tmp_chalice_file)


def test_parser_does_not_support_plain_py(parser: ChaliceParser, tmp_path: Path):
    f = tmp_path / "plain.py"
    f.write_text("def hello(): pass\n")
    assert not parser.supports_file(f)


def test_parser_does_not_support_js(parser: ChaliceParser, tmp_path: Path):
    f = tmp_path / "app.js"
    f.write_text("const express = require('express');\n")
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_paths(routes):
    paths = {r.path for r in routes}
    assert "/" in paths
    assert "/users" in paths
    assert "/users/{user_id}" in paths
    assert "/health" in paths


def test_default_method_is_get(routes):
    index_routes = [r for r in routes if r.path == "/"]
    assert len(index_routes) == 1
    assert index_routes[0].method == "GET"


def test_multiple_methods_expanded(routes):
    user_routes = [r for r in routes if r.path == "/users"]
    methods = {r.method for r in user_routes}
    assert methods == {"GET", "POST"}


def test_three_methods_on_detail(routes):
    detail_routes = [r for r in routes if r.path == "/users/{user_id}"]
    methods = {r.method for r in detail_routes}
    assert methods == {"GET", "PUT", "DELETE"}


def test_source_is_set(routes, tmp_chalice_file: Path):
    for r in routes:
        assert r.source == str(tmp_chalice_file)


def test_parse_directory(parser: ChaliceParser, tmp_path: Path):
    app_file = tmp_path / "app.py"
    app_file.write_text(CHALICE_APP_CONTENT)
    found = parser.parse(tmp_path)
    assert len(found) == len(parser.parse(app_file))
