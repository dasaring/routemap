import pytest
from pathlib import Path
from routemap.parsers.asp_parser import AspParser

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "asp_app"


@pytest.fixture
def parser():
    return AspParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR)


def test_parser_supports_cs_with_map_methods(parser, tmp_path):
    cs = tmp_path / "Program.cs"
    cs.write_text('app.MapGet("/ping", () => "pong");')
    assert parser.supports_file(cs) is True


def test_parser_does_not_support_plain_cs(parser, tmp_path):
    cs = tmp_path / "Util.cs"
    cs.write_text("public class Util { }")
    assert parser.supports_file(cs) is False


def test_parser_does_not_support_js(parser, tmp_path):
    js = tmp_path / "app.js"
    js.write_text('app.get("/", () => {});')
    assert parser.supports_file(js) is False


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_health_route(routes):
    paths = [r.path for r in routes]
    assert "/health" in paths


def test_parser_finds_all_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "DELETE" in methods


def test_route_entries_have_source(routes):
    for route in routes:
        assert route.source is not None
        assert route.source.endswith(".cs")


def test_parser_finds_parameterized_paths(routes):
    paths = [r.path for r in routes]
    assert any("{id}" in p for p in paths)


def test_parser_returns_route_entry_objects(routes):
    from routemap.parsers.base import RouteEntry
    for route in routes:
        assert isinstance(route, RouteEntry)
