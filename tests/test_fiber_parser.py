import pytest
from pathlib import Path
from routemap.parsers.fiber_parser import FiberParser

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "fiber_app"


@pytest.fixture
def parser():
    return FiberParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR / "main.go")


def test_parser_supports_go_with_fiber(parser, tmp_path):
    f = tmp_path / "main.go"
    f.write_text('import "github.com/gofiber/fiber/v2"\napp := fiber.New()')
    assert parser.supports_file(f) is True


def test_parser_does_not_support_plain_go(parser, tmp_path):
    f = tmp_path / "main.go"
    f.write_text('package main\nfunc main() {}')
    assert parser.supports_file(f) is False


def test_parser_does_not_support_python(parser, tmp_path):
    f = tmp_path / "app.py"
    f.write_text("from fastapi import FastAPI")
    assert parser.supports_file(f) is False


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_routes(routes):
    assert len(routes) == 8  # /health + 5 user + 2 product


def test_parser_finds_health_route(routes):
    paths = [r.path for r in routes]
    assert "/health" in paths


def test_parser_finds_user_routes(routes):
    paths = [r.path for r in routes]
    assert "/users" in paths or any("/users" in p for p in paths)


def test_parser_methods_present(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "DELETE" in methods


def test_route_source_is_set(routes):
    for route in routes:
        assert route.source is not None
        assert route.source.endswith(".go")


def test_parser_parses_directory(parser, tmp_path):
    go_file = tmp_path / "server.go"
    go_file.write_text(
        'import "github.com/gofiber/fiber/v2"\n'
        'app := fiber.New()\n'
        'app.Get("/ping", handler)\n'
        'app.Post("/items", handler)\n'
    )
    results = parser.parse(tmp_path)
    assert len(results) == 2
    paths = [r.path for r in results]
    assert "/ping" in paths
    assert "/items" in paths
