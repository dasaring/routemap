import pytest
from pathlib import Path
from textwrap import dedent
from routemap.parsers.gin_parser import GinParser


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "gin_app"


@pytest.fixture
def tmp_gin_file(tmp_path):
    content = dedent("""
        package main

        import "github.com/gin-gonic/gin"

        func main() {
            router := gin.Default()

            router.GET("/health", healthHandler)
            router.GET("/users", listUsers)
            router.POST("/users", createUser)

            v1 := router.Group("/api/v1")
            v1.GET("/items", listItems)
            v1.POST("/items", createItem)
            v1.DELETE("/items/:id", deleteItem)

            router.Run(":8080")
        }
    """)
    f = tmp_path / "main.go"
    f.write_text(content)
    return tmp_path


@pytest.fixture
def parser():
    return GinParser()


@pytest.fixture
def routes(parser, tmp_gin_file):
    return parser.parse(tmp_gin_file)


def test_parser_supports_go_files(parser, tmp_path):
    go_file = tmp_path / "main.go"
    go_file.touch()
    assert parser.supports_file(go_file) is True


def test_parser_does_not_support_js(parser, tmp_path):
    js_file = tmp_path / "app.js"
    js_file.touch()
    assert parser.supports_file(js_file) is False


def test_parser_does_not_support_py(parser, tmp_path):
    py_file = tmp_path / "app.py"
    py_file.touch()
    assert parser.supports_file(py_file) is False


def test_parser_finds_routes(routes):
    assert len(routes) >= 6


def test_parser_finds_health_route(routes):
    paths = [r.path for r in routes]
    assert "/health" in paths


def test_parser_finds_user_routes(routes):
    paths = [r.path for r in routes]
    assert "/users" in paths


def test_parser_finds_all_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "DELETE" in methods


def test_parser_finds_delete_with_param(routes):
    delete_routes = [r for r in routes if r.method == "DELETE"]
    assert any(":id" in r.path for r in delete_routes)


def test_route_has_source_file(routes):
    for route in routes:
        assert route.source_file is not None
        assert route.source_file.endswith(".go")


def test_parse_empty_directory(parser, tmp_path):
    result = parser.parse(tmp_path)
    assert result == []
