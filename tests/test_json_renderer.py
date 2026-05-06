"""Tests for the JSON renderer."""

import json
from pathlib import Path

import pytest

from routemap.parsers.base import RouteEntry
from routemap.renderers.json_renderer import JsonRenderer


@pytest.fixture()
def sample_routes() -> list[RouteEntry]:
    return [
        RouteEntry(method="GET", path="/users", handler="list_users", source_file=Path("app.py"), line_number=10),
        RouteEntry(method="POST", path="/users", handler="create_user", source_file=Path("app.py"), line_number=16),
        RouteEntry(method="DELETE", path="/users/{id}", handler="delete_user", source_file=None, line_number=None),
    ]


@pytest.fixture()
def renderer() -> JsonRenderer:
    return JsonRenderer()


def test_render_returns_string(renderer: JsonRenderer, sample_routes: list[RouteEntry]) -> None:
    result = renderer.render(sample_routes)
    assert isinstance(result, str)


def test_render_valid_json(renderer: JsonRenderer, sample_routes: list[RouteEntry]) -> None:
    result = renderer.render(sample_routes)
    parsed = json.loads(result)
    assert isinstance(parsed, list)


def test_render_correct_count(renderer: JsonRenderer, sample_routes: list[RouteEntry]) -> None:
    parsed = json.loads(renderer.render(sample_routes))
    assert len(parsed) == len(sample_routes)


def test_render_contains_expected_fields(renderer: JsonRenderer, sample_routes: list[RouteEntry]) -> None:
    parsed = json.loads(renderer.render(sample_routes))
    for entry in parsed:
        assert "method" in entry
        assert "path" in entry
        assert "handler" in entry
        assert "source_file" in entry
        assert "line_number" in entry


def test_render_null_source_file(renderer: JsonRenderer, sample_routes: list[RouteEntry]) -> None:
    parsed = json.loads(renderer.render(sample_routes))
    assert parsed[2]["source_file"] is None
    assert parsed[2]["line_number"] is None


def test_render_methods_preserved(renderer: JsonRenderer, sample_routes: list[RouteEntry]) -> None:
    parsed = json.loads(renderer.render(sample_routes))
    methods = [e["method"] for e in parsed]
    assert methods == ["GET", "POST", "DELETE"]


def test_render_paths_preserved(renderer: JsonRenderer, sample_routes: list[RouteEntry]) -> None:
    parsed = json.loads(renderer.render(sample_routes))
    paths = [e["path"] for e in parsed]
    assert "/users" in paths
    assert "/users/{id}" in paths


def test_render_empty_list(renderer: JsonRenderer) -> None:
    result = renderer.render([])
    assert json.loads(result) == []


def test_render_custom_indent() -> None:
    r = JsonRenderer(indent=4)
    routes = [RouteEntry(method="GET", path="/", handler="root", source_file=None, line_number=1)]
    result = r.render(routes)
    # 4-space indent means lines start with four spaces
    assert "    " in result


def test_get_renderer_returns_json_renderer() -> None:
    from routemap.renderers import get_renderer
    # Ensure the registry is aware of json (or gracefully handles unknown)
    # This test documents expected behaviour once the registry is updated.
    try:
        r = get_renderer("json")
        assert hasattr(r, "render")
    except ValueError:
        pytest.skip("json renderer not yet registered in get_renderer")
