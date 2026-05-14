import pytest
from pathlib import Path
from routemap.parsers.phoenix_parser import PhoenixParser


FIXTURE_DIR = Path("tests/fixtures/phoenix_app")


@pytest.fixture
def parser():
    return PhoenixParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR)


def test_parser_supports_phoenix_ex(parser, tmp_path):
    f = tmp_path / "router.ex"
    f.write_text('defmodule MyAppWeb.Router do\n  use Phoenix.Router\nend\n')
    assert parser.supports_file(f)


def test_parser_does_not_support_plain_ex(parser, tmp_path):
    f = tmp_path / "helper.ex"
    f.write_text('defmodule MyApp.Helper do\n  def greet, do: :ok\nend\n')
    assert not parser.supports_file(f)


def test_parser_does_not_support_js(parser, tmp_path):
    f = tmp_path / "app.js"
    f.write_text('const express = require("express");')
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_explicit_get_routes(routes):
    get_routes = [r for r in routes if r.method == "GET"]
    assert any(r.path == "/health" for r in get_routes)
    assert any(r.path == "/users" for r in get_routes)
    assert any(r.path == "/users/:id" for r in get_routes)


def test_parser_finds_post_route(routes):
    post_routes = [r for r in routes if r.method == "POST"]
    assert any(r.path == "/users" for r in post_routes)


def test_parser_finds_delete_route(routes):
    delete_routes = [r for r in routes if r.method == "DELETE"]
    assert any(r.path == "/users/:id" for r in delete_routes)


def test_parser_expands_resources(routes):
    # resources "/posts" should generate multiple routes
    post_routes = [r for r in routes if "/posts" in r.path]
    methods = {r.method for r in post_routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "DELETE" in methods


def test_parser_sets_handler(routes):
    health = next((r for r in routes if r.path == "/health"), None)
    assert health is not None
    assert "HealthController" in health.handler


def test_parser_sets_source(routes):
    for route in routes:
        assert "router.ex" in route.source
