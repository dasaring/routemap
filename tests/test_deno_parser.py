import pytest
from pathlib import Path
from routemap.parsers.deno_parser import DenoParser

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "deno_app"


@pytest.fixture
def parser():
    return DenoParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR / "server.ts")


def test_parser_supports_ts_with_oak(parser, tmp_path):
    f = tmp_path / "server.ts"
    f.write_text('import { Router } from "https://deno.land/x/oak/mod.ts";\nrouter.get("/", h);')
    assert parser.supports_file(f)


def test_parser_does_not_support_plain_ts(parser, tmp_path):
    f = tmp_path / "app.ts"
    f.write_text('const x = 1;')
    assert not parser.supports_file(f)


def test_parser_does_not_support_python(parser, tmp_path):
    f = tmp_path / "app.py"
    f.write_text('import oak')
    assert not parser.supports_file(f)


def test_parser_does_not_support_plain_js(parser, tmp_path):
    f = tmp_path / "app.js"
    f.write_text('console.log("hello");')
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_routes(routes):
    assert len(routes) == 6


def test_route_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "DELETE" in methods


def test_route_paths(routes):
    paths = {r.path for r in routes}
    assert "/users" in paths
    assert "/users/:id" in paths
    assert "/health" in paths


def test_route_source(routes):
    for route in routes:
        assert "server.ts" in route.source


def test_parse_directory(parser, tmp_path):
    f = tmp_path / "app.ts"
    f.write_text(
        'import { Router } from "https://deno.land/x/oak/mod.ts";\n'
        'router.get("/items", h);\n'
        'router.post("/items", h);\n'
    )
    routes = parser.parse(tmp_path)
    assert len(routes) == 2


def test_parse_nonexistent_file(parser, tmp_path):
    routes = parser.parse(tmp_path / "missing.ts")
    assert routes == []
