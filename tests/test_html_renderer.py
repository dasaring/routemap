import pytest
from routemap.renderers.html_renderer import HtmlRenderer
from routemap.parsers.base import RouteEntry


@pytest.fixture
def sample_routes():
    return [
        RouteEntry(method="GET", path="/users", handler="list_users", source_file="app.py"),
        RouteEntry(method="POST", path="/users", handler="create_user", source_file="app.py"),
        RouteEntry(method="DELETE", path="/users/{id}", handler="delete_user", source_file="app.py"),
        RouteEntry(method="GET", path="/items", handler="list_items", source_file="items.py"),
        RouteEntry(method="PUT", path="/items/{id}", handler="update_item", source_file="items.py"),
    ]


@pytest.fixture
def renderer():
    return HtmlRenderer()


def test_render_returns_string(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert isinstance(result, str)


def test_render_is_valid_html(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert result.startswith("<!DOCTYPE html>")
    assert "</html>" in result


def test_render_contains_all_paths(renderer, sample_routes):
    result = renderer.render(sample_routes)
    for route in sample_routes:
        assert route.path in result


def test_render_contains_all_methods(renderer, sample_routes):
    result = renderer.render(sample_routes)
    for route in sample_routes:
        assert route.method.upper() in result


def test_render_contains_handlers(renderer, sample_routes):
    result = renderer.render(sample_routes)
    for route in sample_routes:
        assert route.handler in result


def test_render_groups_by_source(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert "app.py" in result
    assert "items.py" in result


def test_render_custom_title():
    r = HtmlRenderer(title="My Custom API")
    result = r.render([])
    assert "My Custom API" in result
    assert "<title>My Custom API</title>" in result


def test_render_default_title(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert "API Route Map" in result


def test_render_method_badges(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert 'class="badge"' in result


def test_render_empty_routes(renderer):
    result = renderer.render([])
    assert isinstance(result, str)
    assert "<!DOCTYPE html>" in result


def test_get_renderer_html():
    from routemap.renderers import get_renderer
    r = get_renderer("html")
    assert isinstance(r, HtmlRenderer)
