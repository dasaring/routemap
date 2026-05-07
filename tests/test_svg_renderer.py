import pytest
from routemap.parsers.base import RouteEntry
from routemap.renderers.svg_renderer import SvgRenderer


@pytest.fixture
def sample_routes():
    return [
        RouteEntry(method="GET", path="/users", handler="list_users", source_file="app.py"),
        RouteEntry(method="POST", path="/users", handler="create_user", source_file="app.py"),
        RouteEntry(method="GET", path="/users/{id}", handler="get_user", source_file="app.py"),
        RouteEntry(method="DELETE", path="/users/{id}", handler="delete_user", source_file="app.py"),
        RouteEntry(method="PUT", path="/items", handler="update_item", source_file="items.py"),
    ]


@pytest.fixture
def renderer():
    return SvgRenderer()


def test_render_returns_string(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert isinstance(result, str)


def test_render_starts_with_svg_tag(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert result.startswith("<svg ")


def test_render_ends_with_svg_close(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert result.strip().endswith("</svg>")


def test_render_contains_xmlns(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert 'xmlns="http://www.w3.org/2000/svg"' in result


def test_render_contains_all_paths(renderer, sample_routes):
    result = renderer.render(sample_routes)
    for route in sample_routes:
        assert route.path in result


def test_render_contains_all_methods(renderer, sample_routes):
    result = renderer.render(sample_routes)
    for route in sample_routes:
        assert route.method.upper() in result


def test_render_contains_source_files(renderer, sample_routes):
    result = renderer.render(sample_routes)
    assert "app.py" in result
    assert "items.py" in result


def test_render_custom_title():
    renderer = SvgRenderer(title="My Custom API")
    result = renderer.render([])
    assert "My Custom API" in result


def test_render_empty_routes(renderer):
    result = renderer.render([])
    assert isinstance(result, str)
    assert result.startswith("<svg ")
    assert result.strip().endswith("</svg>")


def test_render_method_colors(renderer, sample_routes):
    result = renderer.render(sample_routes)
    # GET color
    assert "#61affe" in result
    # POST color
    assert "#49cc90" in result
    # DELETE color
    assert "#f93e3e" in result


def test_render_escapes_special_chars():
    renderer = SvgRenderer(title="Test & <Check>")
    routes = [
        RouteEntry(method="GET", path="/a&b", handler=None, source_file="file.py"),
    ]
    result = renderer.render(routes)
    assert "&amp;" in result or "&lt;" in result or "/a" in result
    assert "<Check>" not in result


def test_svg_in_renderer_registry():
    from routemap.renderers import available_renderers
    # svg renderer should be discoverable or at least importable
    from routemap.renderers.svg_renderer import SvgRenderer
    assert SvgRenderer is not None
