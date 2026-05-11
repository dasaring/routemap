import pytest
from pathlib import Path
from routemap.parsers.laravel_parser import LaravelParser

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "laravel_app"


@pytest.fixture
def parser():
    return LaravelParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR)


def test_parser_supports_api_php(parser):
    assert parser.supports_file(Path("routes/api.php"))


def test_parser_supports_web_php(parser):
    assert parser.supports_file(Path("routes/web.php"))


def test_parser_supports_php_in_routes_dir(parser):
    assert parser.supports_file(Path("routes/custom.php"))


def test_parser_does_not_support_js(parser):
    assert not parser.supports_file(Path("app.js"))


def test_parser_does_not_support_arbitrary_php(parser):
    assert not parser.supports_file(Path("app/Http/Controllers/UserController.php"))


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_explicit_get(routes):
    paths = [r.path for r in routes]
    assert "/users" in paths


def test_parser_finds_explicit_delete(routes):
    methods = {r.method for r in routes}
    assert "DELETE" in methods


def test_parser_expands_resource_routes(routes):
    resource_routes = [r for r in routes if r.path.startswith("/posts")]
    assert len(resource_routes) == 7


def test_resource_routes_include_all_methods(routes):
    resource_routes = [r for r in routes if r.path.startswith("/posts")]
    methods = {r.method for r in resource_routes}
    assert methods == {"GET", "POST", "PUT", "DELETE"}


def test_route_paths_start_with_slash(routes):
    for route in routes:
        assert route.path.startswith("/"), f"Path missing leading slash: {route.path}"


def test_source_is_set(routes):
    for route in routes:
        assert route.source and "api.php" in route.source
