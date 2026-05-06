import pytest
from routemap.parsers.base import RouteEntry
from routemap.renderers.mermaid_renderer import MermaidRenderer


@pytest.fixture
def sample_routes():
    return [
        RouteEntry(method="GET", path="/users", handler="getUsers", source_file="routes/users.py"),
        RouteEntry(method="POST", path="/users", handler="createUser", source_file="routes/users.py"),
        RouteEntry(method="DELETE", path="/users/{id}", handler="deleteUser", source_file="routes/users.py"),
        RouteEntry(method="GET", path="/items", handler="getItems", source_file="routes/items.py"),
    ]


@pytest.fixture
def renderer():
    return MermaidRenderer()


def test_render_returns_string(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert isinstance(result, str)


def test_render_starts_with_graph(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert result.startswith("graph LR")


def test_render_custom_direction():
    renderer = MermaidRenderer(direction="TD")
    routes = [RouteEntry(method="GET", path="/ping", handler="ping", source_file="app.py")]
    result = renderer.render(routes)
    assert result.startswith("graph TD")


def test_render_contains_paths(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert "/users" in result
    assert "/items" in result
    assert "/users/{id}" in result


def test_render_contains_methods(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert "GET" in result
    assert "POST" in result
    assert "DELETE" in result


def test_render_contains_source_files(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert "users.py" in result
    assert "items.py" in result


def test_render_contains_class_definitions(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert "classDef methodGET" in result
    assert "classDef methodPOST" in result
    assert "classDef methodDELETE" in result


def test_render_empty_routes(renderer):
    result = renderer.render([])
    assert result.strip().startswith("graph LR")


def test_render_deduplicates_nodes(renderer):
    routes = [
        RouteEntry(method="GET", path="/ping", handler="ping1", source_file="app.py"),
        RouteEntry(method="GET", path="/ping", handler="ping2", source_file="app.py"),
    ]
    result = renderer.render(routes)
    assert result.count("GET /ping") == 1
