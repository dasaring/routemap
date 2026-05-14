import pytest
from pathlib import Path
from routemap.parsers.nestjs_parser import NestJSParser

FIXTURES = Path(__file__).parent / "fixtures" / "nestjs_app"


@pytest.fixture
def parser():
    return NestJSParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURES)


def test_parser_supports_ts_with_controller(parser, tmp_path):
    f = tmp_path / "app.controller.ts"
    f.write_text("import { Controller, Get } from '@nestjs/common';\n@Controller('x')\nexport class X {}")
    assert parser.supports_file(f)


def test_parser_does_not_support_js(parser, tmp_path):
    f = tmp_path / "app.js"
    f.write_text("console.log('hello')")
    assert not parser.supports_file(f)


def test_parser_does_not_support_plain_ts(parser, tmp_path):
    f = tmp_path / "service.ts"
    f.write_text("export class MyService {}")
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_user_routes(routes):
    user_routes = [r for r in routes if "/users" in r.path]
    assert len(user_routes) >= 5


def test_parser_finds_health_routes(routes):
    health_routes = [r for r in routes if "/health" in r.path]
    assert len(health_routes) >= 2


def test_route_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "DELETE" in methods


def test_route_paths_start_with_slash(routes):
    for route in routes:
        assert route.path.startswith("/"), f"Path {route.path!r} should start with /"


def test_route_has_source(routes):
    for route in routes:
        assert route.source is not None
        assert route.source.endswith(".ts")


def test_health_ready_path(routes):
    paths = [r.path for r in routes]
    assert "/health/ready" in paths
