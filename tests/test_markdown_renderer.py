import pytest
from routemap.parsers.base import RouteEntry
from routemap.renderers.markdown_renderer import MarkdownRenderer


@pytest.fixture
def sample_routes():
    return [
        RouteEntry(method="GET", path="/users", source_file="app/routes.py", name="list_users"),
        RouteEntry(method="POST", path="/users", source_file="app/routes.py", name="create_user"),
        RouteEntry(method="DELETE", path="/users/{id}", source_file="app/routes.py", name="delete_user"),
        RouteEntry(method="GET", path="/items", source_file="app/items.py", name="list_items"),
    ]


@pytest.fixture
def renderer():
    return MarkdownRenderer()


def test_render_returns_string(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert isinstance(result, str)


def test_render_starts_with_heading(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert result.startswith("# API Route Map")


def test_render_custom_title():
    r = MarkdownRenderer(title="My Custom API")
    result = r.render([])
    assert "# My Custom API" in result


def test_render_contains_all_paths(renderer, sample_routes):
    result = renderer.render(sample_routes)
    for route in sample_routes:
        assert route.path in result


def test_render_contains_all_methods(renderer, sample_routes):
    result = renderer.render(sample_routes)
    for route in sample_routes:
        assert route.method.upper() in result


def test_render_groups_by_source(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert "## `app/routes.py`" in result
    assert "## `app/items.py`" in result


def test_render_contains_table_headers(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert "| Method | Path | Name |" in result
    assert "|--------|------|------|" in result


def test_render_contains_route_names(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert "list_users" in result
    assert "create_user" in result


def test_render_shows_dash_for_missing_name(renderer):
    routes = [RouteEntry(method="GET", path="/health", source_file="app.py", name=None)]
    result = renderer.render(routes)
    assert "—" in result


def test_render_route_count_in_summary(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert "4 route(s) found" in result
