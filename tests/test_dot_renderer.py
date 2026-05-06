"""Tests for the Graphviz DOT renderer."""
import pytest
from routemap.parsers.base import RouteEntry
from routemap.renderers.dot_renderer import DotRenderer


@pytest.fixture
def sample_routes():
    return [
        RouteEntry(method="GET", path="/users", source_file="app.py", line_number=10),
        RouteEntry(method="POST", path="/users", source_file="app.py", line_number=15),
        RouteEntry(method="DELETE", path="/users/{id}", source_file="app.py", line_number=20),
        RouteEntry(method="GET", path="/items", source_file="items.py", line_number=5),
        RouteEntry(method="PUT", path="/items/{id}", source_file="items.py", line_number=12),
    ]


@pytest.fixture
def renderer():
    return DotRenderer()


def test_render_returns_string(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert isinstance(result, str)


def test_render_starts_with_digraph(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert result.strip().startswith("digraph routemap {")


def test_render_ends_with_brace(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert result.strip().endswith("}")


def test_render_contains_all_paths(renderer, sample_routes):
    result = renderer.render(sample_routes)
    for route in sample_routes:
        assert route.path in result


def test_render_contains_all_methods(renderer, sample_routes):
    result = renderer.render(sample_routes)
    for route in sample_routes:
        assert route.method in result


def test_render_contains_subgraphs(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert "subgraph cluster_" in result
    assert 'label="app.py"' in result
    assert 'label="items.py"' in result


def test_render_custom_rankdir():
    renderer = DotRenderer(rankdir="TB")
    routes = [RouteEntry(method="GET", path="/", source_file="main.py", line_number=1)]
    result = renderer.render(routes)
    assert "rankdir=TB" in result


def test_render_concentrate_false():
    renderer = DotRenderer(concentrate=False)
    routes = [RouteEntry(method="GET", path="/", source_file="main.py", line_number=1)]
    result = renderer.render(routes)
    assert "concentrate=false" in result


def test_render_method_colors(renderer, sample_routes):
    result = renderer.render(sample_routes)
    # GET should use its defined color
    assert "#61affe" in result
    # DELETE should use its defined color
    assert "#f93e3e" in result


def test_render_empty_routes(renderer):
    result = renderer.render([])
    assert "digraph routemap {" in result
    assert result.strip().endswith("}")


def test_safe_id_replaces_special_chars(renderer):
    result = renderer._safe_id("/users/{id}")
    assert "/" not in result
    assert "{" not in result
    assert "}" not in result
