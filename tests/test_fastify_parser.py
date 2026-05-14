import pytest
from pathlib import Path
from routemap.parsers.fastify_parser import FastifyParser

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "fastify_app"


@pytest.fixture
def parser():
    return FastifyParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR / "server.js")


def test_parser_supports_js_with_fastify(parser, tmp_path):
    f = tmp_path / "server.js"
    f.write_text("const fastify = require('fastify')();\n")
    assert parser.supports_file(f) is True


def test_parser_does_not_support_plain_js(parser, tmp_path):
    f = tmp_path / "app.js"
    f.write_text("console.log('hello');\n")
    assert parser.supports_file(f) is False


def test_parser_does_not_support_python(parser, tmp_path):
    f = tmp_path / "app.py"
    f.write_text("import fastapi\n")
    assert parser.supports_file(f) is False


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_routes(routes):
    # 5 shorthand + 2 object-style
    assert len(routes) == 7


def test_parser_finds_get_users(routes):
    paths = [r.path for r in routes]
    assert "/users" in paths


def test_parser_finds_health(routes):
    paths = [r.path for r in routes]
    assert "/health" in paths


def test_parser_finds_auth_login(routes):
    paths = [r.path for r in routes]
    assert "/auth/login" in paths


def test_parser_finds_all_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "DELETE" in methods


def test_route_source_is_set(routes):
    for route in routes:
        assert route.source is not None
        assert "server.js" in route.source


def test_parser_handles_directory(parser):
    result = parser.parse(FIXTURE_DIR)
    assert len(result) == 7


def test_parser_handles_missing_file(parser, tmp_path):
    result = parser.parse(tmp_path / "nonexistent.js")
    assert result == []
