import pytest
from pathlib import Path

from routemap.parsers.express_parser import ExpressParser


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "express_app"


@pytest.fixture
def parser() -> ExpressParser:
    return ExpressParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURES_DIR)


def test_parser_supports_js_files(parser):
    assert parser.supports_file(Path("app.js"))
    assert parser.supports_file(Path("routes.ts"))
    assert parser.supports_file(Path("server.mjs"))
    assert not parser.supports_file(Path("app.py"))


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "PATCH" in methods
    assert "DELETE" in methods


def test_app_level_routes(routes):
    app_routes = [r for r in routes if "app.js" in r.source_file]
    paths = [r.path for r in app_routes]
    assert "/health" in paths
    assert "/version" in paths
    assert "/login" in paths


def test_router_level_routes(routes):
    router_routes = [r for r in routes if "users.js" in r.source_file]
    paths = [r.path for r in router_routes]
    assert "/users" in paths
    assert "/users/:id" in paths


def test_chained_route_methods(routes):
    chained = [r for r in routes if r.path == "/users/:id" and "users.js" in r.source_file]
    methods = {r.method for r in chained}
    # Chained: PUT, PATCH, DELETE; plus individual GET
    assert "PUT" in methods
    assert "PATCH" in methods
    assert "DELETE" in methods


def test_route_entry_repr(routes):
    r = routes[0]
    assert r.method in repr(r)
    assert r.path in repr(r)


def test_line_numbers_are_positive(routes):
    for route in routes:
        assert route.line_number > 0
