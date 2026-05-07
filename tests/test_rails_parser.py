import pytest
from pathlib import Path
from routemap.parsers.rails_parser import RailsParser


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "rails_app"


@pytest.fixture
def parser():
    return RailsParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR)


def test_parser_supports_routes_rb(parser):
    assert parser.supports_file(Path("config/routes.rb"))


def test_parser_does_not_support_other_rb(parser):
    assert not parser.supports_file(Path("app/models/user.rb"))


def test_parser_does_not_support_js(parser):
    assert not parser.supports_file(Path("routes.js"))


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_explicit_get_route(routes):
    paths = [r.path for r in routes]
    assert "/health" in paths


def test_explicit_patch_route(routes):
    entry = next((r for r in routes if r.path == "/settings"), None)
    assert entry is not None
    assert entry.method == "PATCH"


def test_resource_routes_expanded(routes):
    user_routes = [r for r in routes if r.path in ("/users", "/users/:id")]
    methods = {r.method for r in user_routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "DELETE" in methods


def test_namespace_prefix_applied(routes):
    api_paths = [r.path for r in routes if r.path.startswith("/api/")]
    assert len(api_paths) > 0


def test_namespace_stats_route(routes):
    entry = next((r for r in routes if r.path == "/api/stats"), None)
    assert entry is not None
    assert entry.method == "GET"


def test_source_field_set(routes):
    for route in routes:
        assert route.source != ""
        assert "routes.rb" in route.source


def test_handler_field_set_for_explicit_routes(routes):
    health = next((r for r in routes if r.path == "/health"), None)
    assert health is not None
    assert health.handler == "health#check"
