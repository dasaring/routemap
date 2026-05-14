import pytest
from pathlib import Path
from routemap.parsers.sanic_parser import SanicParser


FIXTURE_PATH = Path("tests/fixtures/sanic_app/app.py")


@pytest.fixture
def parser():
    return SanicParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_PATH)


def test_parser_supports_sanic_py(parser, tmp_path):
    f = tmp_path / "app.py"
    f.write_text("from sanic import Sanic\napp = Sanic('test')\n")
    assert parser.supports_file(f) is True


def test_parser_supports_import_sanic(parser, tmp_path):
    f = tmp_path / "server.py"
    f.write_text("import sanic\n")
    assert parser.supports_file(f) is True


def test_parser_does_not_support_plain_py(parser, tmp_path):
    f = tmp_path / "utils.py"
    f.write_text("def helper():\n    pass\n")
    assert parser.supports_file(f) is False


def test_parser_does_not_support_js(parser, tmp_path):
    f = tmp_path / "app.js"
    f.write_text("const sanic = require('sanic');\n")
    assert parser.supports_file(f) is False


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_paths(routes):
    paths = {r.path for r in routes}
    assert "/health" in paths
    assert "/users" in paths
    assert "/users/<user_id:int>" in paths
    assert "/items" in paths


def test_parser_finds_all_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "DELETE" in methods


def test_route_multi_method(routes):
    item_routes = [r for r in routes if r.path == "/items"]
    methods = {r.method for r in item_routes}
    assert "GET" in methods
    assert "POST" in methods


def test_route_source_is_set(routes):
    for route in routes:
        assert route.source
        assert "sanic_app" in route.source


def test_parse_directory(parser, tmp_path):
    app_file = tmp_path / "app.py"
    app_file.write_text(
        "from sanic import Sanic\n"
        "app = Sanic('test')\n"
        "@app.get('/ping')\n"
        "async def ping(request): pass\n"
    )
    routes = parser.parse(tmp_path)
    assert any(r.path == "/ping" for r in routes)


def test_parse_missing_file(parser, tmp_path):
    missing = tmp_path / "nonexistent.py"
    routes = parser.parse(missing)
    assert routes == []
