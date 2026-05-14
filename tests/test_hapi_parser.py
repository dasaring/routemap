import pytest
from pathlib import Path
from routemap.parsers.hapi_parser import HapiParser

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "hapi_app"


@pytest.fixture
def parser():
    return HapiParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR)


def test_parser_supports_hapi_js(parser, tmp_path):
    f = tmp_path / "server.js"
    f.write_text('const Hapi = require("@hapi/hapi");\nserver.route({ method: "GET", path: "/" });')
    assert parser.supports_file(f)


def test_parser_supports_ts_with_hapi(parser, tmp_path):
    f = tmp_path / "server.ts"
    f.write_text("import Hapi from '@hapi/hapi';\nserver.route({ method: 'GET', path: '/health' });")
    assert parser.supports_file(f)


def test_parser_does_not_support_plain_js(parser, tmp_path):
    f = tmp_path / "app.js"
    f.write_text("console.log('hello');")
    assert not parser.supports_file(f)


def test_parser_does_not_support_python(parser, tmp_path):
    f = tmp_path / "app.py"
    f.write_text("import hapi\nserver.route('GET', '/users')")
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_routes(routes):
    # GET /users, POST /users, GET /users/{id}, PUT /users/{id},
    # PATCH /users/{id}, DELETE /users/{id}, GET /health = 7 total
    assert len(routes) == 7


def test_route_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "PATCH" in methods
    assert "DELETE" in methods


def test_route_paths(routes):
    paths = {r.path for r in routes}
    assert "/users" in paths
    assert "/users/{id}" in paths
    assert "/health" in paths


def test_multi_method_route_expanded(routes):
    """PUT and PATCH on same path should be separate RouteEntry objects."""
    update_routes = [r for r in routes if r.path == "/users/{id}"]
    update_methods = {r.method for r in update_routes}
    assert "PUT" in update_methods
    assert "PATCH" in update_methods


def test_route_source_is_set(routes):
    for route in routes:
        assert route.source
        assert "server.js" in route.source


def test_route_repr(routes):
    for route in routes:
        r = repr(route)
        assert route.method in r
        assert route.path in r
