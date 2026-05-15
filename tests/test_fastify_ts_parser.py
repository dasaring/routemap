import pytest
from pathlib import Path
from routemap.parsers.fastify_ts_parser import FastifyTSParser


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "fastify_ts_app" / "src"


@pytest.fixture
def parser():
    return FastifyTSParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR / "server.ts")


def test_parser_supports_ts_with_fastify(parser, tmp_path):
    f = tmp_path / "server.ts"
    f.write_text("import fastify from 'fastify';\napp.get('/ping', handler);")
    assert parser.supports_file(f)


def test_parser_supports_js_with_fastify(parser, tmp_path):
    f = tmp_path / "server.js"
    f.write_text("const fastify = require('fastify')();\nfastify.get('/ping', handler);")
    assert parser.supports_file(f)


def test_parser_does_not_support_plain_ts(parser, tmp_path):
    f = tmp_path / "utils.ts"
    f.write_text("export const add = (a: number, b: number) => a + b;")
    assert not parser.supports_file(f)


def test_parser_does_not_support_python(parser, tmp_path):
    f = tmp_path / "app.py"
    f.write_text("from fastapi import FastAPI")
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "DELETE" in methods


def test_parser_finds_chained_routes(routes):
    paths = [r.path for r in routes]
    assert "/users" in paths
    assert "/users/:id" in paths
    assert "/health" in paths


def test_parser_finds_object_style_routes(routes):
    paths = [r.path for r in routes]
    assert "/status" in paths
    assert "/items" in paths


def test_parser_object_style_method(routes):
    status_routes = [r for r in routes if r.path == "/status"]
    assert len(status_routes) == 1
    assert status_routes[0].method == "GET"

    item_routes = [r for r in routes if r.path == "/items"]
    assert len(item_routes) == 1
    assert item_routes[0].method == "POST"


def test_route_source_is_set(routes):
    for route in routes:
        assert route.source is not None
        assert "server.ts" in route.source


def test_parse_directory(parser, tmp_path):
    f = tmp_path / "app.ts"
    f.write_text(
        "import fastify from 'fastify';\n"
        "const app = fastify();\n"
        "app.get('/ping', async () => 'pong');\n"
        "app.post('/data', async () => ({}));\n"
    )
    results = parser.parse(tmp_path)
    assert len(results) == 2
    paths = [r.path for r in results]
    assert "/ping" in paths
    assert "/data" in paths
