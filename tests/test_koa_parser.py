import pytest
from pathlib import Path
from routemap.parsers.koa_parser import KoaParser


FIXTURES = Path(__file__).parent / "fixtures" / "koa_app"


@pytest.fixture
def parser():
    return KoaParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURES)


def test_parser_supports_js_with_koa_router(parser, tmp_path):
    f = tmp_path / "app.js"
    f.write_text("const Router = require('koa-router');\nrouter.get('/x', fn);")
    assert parser.supports_file(f)


def test_parser_supports_ts_with_koa_router(parser, tmp_path):
    f = tmp_path / "app.ts"
    f.write_text("import Router from '@koa/router';\nrouter.get('/x', fn);")
    assert parser.supports_file(f)


def test_parser_does_not_support_plain_js(parser, tmp_path):
    f = tmp_path / "plain.js"
    f.write_text("console.log('hello');")
    assert not parser.supports_file(f)


def test_parser_does_not_support_python(parser, tmp_path):
    f = tmp_path / "app.py"
    f.write_text("import koa_router")
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "DELETE" in methods


def test_del_normalized_to_delete(routes):
    methods = {r.method for r in routes}
    assert "DEL" not in methods
    assert "DELETE" in methods


def test_route_paths_are_strings(routes):
    for r in routes:
        assert isinstance(r.path, str)
        assert r.path.startswith("/")


def test_route_source_is_set(routes):
    for r in routes:
        assert r.source
        assert r.source.endswith(".js")


def test_put_and_patch_detected(parser, tmp_path):
    f = tmp_path / "app.js"
    f.write_text(
        "const Router = require('koa-router');\n"
        "router.put('/items/:id', fn);\n"
        "router.patch('/items/:id', fn);\n"
    )
    found = parser._parse_file(f)
    methods = {r.method for r in found}
    assert "PUT" in methods
    assert "PATCH" in methods
