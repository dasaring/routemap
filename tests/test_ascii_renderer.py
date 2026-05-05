import os
import pytest
from routemap.parsers.base import RouteEntry
from routemap.renderers.ascii_renderer import AsciiRenderer


@pytest.fixture
def sample_routes():
    return [
        RouteEntry(method="GET", path="/users", handler="getUsers", source_file="routes/users.js"),
        RouteEntry(method="POST", path="/users", handler="createUser", source_file="routes/users.js"),
        RouteEntry(method="DELETE", path="/users/:id", handler="deleteUser", source_file="routes/users.js"),
        RouteEntry(method="GET", path="/items", handler="list_items", source_file="routers/items.py"),
        RouteEntry(method="PUT", path="/items/{id}", handler="update_item", source_file="routers/items.py"),
    ]


@pytest.fixture
def renderer():
    return AsciiRenderer(use_color=False)


def test_render_returns_string(renderer, sample_routes):
    output = renderer.render(sample_routes)
    assert isinstance(output, str)


def test_render_contains_all_paths(renderer, sample_routes):
    output = renderer.render(sample_routes)
    for route in sample_routes:
        assert route.path in output


def test_render_contains_all_methods(renderer, sample_routes):
    output = renderer.render(sample_routes)
    for route in sample_routes:
        assert route.method.upper() in output


def test_render_contains_handlers(renderer, sample_routes):
    output = renderer.render(sample_routes)
    for route in sample_routes:
        assert route.handler in output


def test_render_groups_by_source(renderer, sample_routes):
    output = renderer.render(sample_routes)
    assert "routes/users.js" in output
    assert "routers/items.py" in output


def test_render_shows_total_count(renderer, sample_routes):
    output = renderer.render(sample_routes)
    assert "Total routes: 5" in output


def test_render_empty_routes(renderer):
    output = renderer.render([])
    assert output == "No routes found."


def test_render_no_handler(renderer):
    routes = [RouteEntry(method="GET", path="/ping", handler=None, source_file="app.py")]
    output = renderer.render(routes)
    assert "/ping" in output
    assert "→" not in output


def test_render_to_file(renderer, sample_routes, tmp_path):
    output_file = tmp_path / "routemap_output.txt"
    renderer.render_to_file(sample_routes, str(output_file))
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "/users" in content
    assert "\033[" not in content  # no ANSI codes in file output


def test_color_mode_does_not_affect_structure(sample_routes):
    plain = AsciiRenderer(use_color=False).render(sample_routes)
    colored = AsciiRenderer(use_color=True).render(sample_routes)
    # Strip ANSI from colored output and compare structure
    import re
    stripped = re.sub(r"\033\[[0-9;]*m", "", colored)
    assert plain == stripped
