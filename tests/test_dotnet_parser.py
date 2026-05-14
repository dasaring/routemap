import pytest
from pathlib import Path
from routemap.parsers.dotnet_parser import DotNetParser


FIXTURES = Path(__file__).parent / "fixtures" / "dotnet_app"


@pytest.fixture
def parser():
    return DotNetParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURES)


def test_parser_supports_cs_with_map_methods(parser, tmp_path):
    f = tmp_path / "prog.cs"
    f.write_text('app.MapGet("/ping", () => "pong");')
    assert parser.supports_file(f)


def test_parser_supports_cs_with_http_attributes(parser, tmp_path):
    f = tmp_path / "ctrl.cs"
    f.write_text('[HttpGet("items")] public IActionResult Get() {}')
    assert parser.supports_file(f)


def test_parser_does_not_support_plain_cs(parser, tmp_path):
    f = tmp_path / "service.cs"
    f.write_text("public class MyService { public void DoWork() {} }")
    assert not parser.supports_file(f)


def test_parser_does_not_support_js(parser, tmp_path):
    f = tmp_path / "app.js"
    f.write_text('app.get("/", (req, res) => res.send("hi"));')
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_minimal_api_routes(routes):
    paths = [r.path for r in routes]
    assert "/health" in paths
    assert "/items" in paths
    assert "/items/{id}" in paths


def test_parser_finds_all_http_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "DELETE" in methods


def test_parser_finds_controller_routes(routes):
    paths = [r.path for r in routes]
    # Controller routes from UsersController
    assert any("users" in p.lower() for p in paths)


def test_route_sources_are_strings(routes):
    for route in routes:
        assert isinstance(route.source, str)
        assert route.source.endswith(".cs")


def test_parser_returns_route_entries_with_required_fields(routes):
    for route in routes:
        assert route.method
        assert route.path
        assert route.path.startswith("/")
