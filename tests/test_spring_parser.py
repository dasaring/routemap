import pytest
from pathlib import Path
from routemap.parsers.spring_parser import SpringParser

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "spring_app"


@pytest.fixture
def parser():
    return SpringParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR)


def test_parser_supports_java(parser):
    assert parser.supports_file(Path("UserController.java"))


def test_parser_supports_kotlin(parser):
    assert parser.supports_file(Path("UserController.kt"))


def test_parser_does_not_support_js(parser):
    assert not parser.supports_file(Path("app.js"))


def test_parser_does_not_support_py(parser):
    assert not parser.supports_file(Path("app.py"))


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "DELETE" in methods


def test_class_level_prefix_applied(routes):
    user_routes = [r for r in routes if "/api/users" in r.path]
    assert len(user_routes) >= 5


def test_health_route_no_prefix(routes):
    health_routes = [r for r in routes if r.path == "/health"]
    assert len(health_routes) == 1


def test_route_entry_has_source(routes):
    for route in routes:
        assert route.source is not None
        assert route.source.endswith(".java")


def test_parser_skips_non_controllers(parser, tmp_path):
    plain = tmp_path / "Service.java"
    plain.write_text('public class Service { public void doThing() {} }')
    result = parser.parse(tmp_path)
    assert result == []
