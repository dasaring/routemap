"""Tests for the FastAPI route parser."""

import os
import textwrap
import tempfile
import pytest

from routemap.parsers.fastapi_parser import FastAPIParser
from routemap.parsers.base import RouteEntry


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary FastAPI project with sample route files."""
    routes_file = tmp_path / "routes.py"
    routes_file.write_text(textwrap.dedent("""
        from fastapi import APIRouter

        router = APIRouter()

        @router.get("/users", tags=["users"], summary="List users")
        async def list_users():
            pass

        @router.post("/users", tags=["users"])
        async def create_user():
            pass

        @router.delete("/users/{user_id}")
        def delete_user(user_id: int):
            pass
    """))
    return tmp_path


def test_parser_finds_routes(tmp_project):
    parser = FastAPIParser(str(tmp_project))
    routes = parser.parse()
    assert len(routes) == 3


def test_route_methods(tmp_project):
    parser = FastAPIParser(str(tmp_project))
    methods = {r.method for r in parser.parse()}
    assert methods == {"GET", "POST", "DELETE"}


def test_route_paths(tmp_project):
    parser = FastAPIParser(str(tmp_project))
    paths = {r.path for r in parser.parse()}
    assert "/users" in paths
    assert "/users/{user_id}" in paths


def test_route_tags_and_summary(tmp_project):
    parser = FastAPIParser(str(tmp_project))
    routes = {r.handler: r for r in parser.parse()}
    assert routes["list_users"].tags == ["users"]
    assert routes["list_users"].summary == "List users"
    assert routes["delete_user"].tags == []
    assert routes["delete_user"].summary is None


def test_supports_file():
    parser = FastAPIParser(".")
    assert parser.supports_file("app.py")
    assert not parser.supports_file("app.js")


def test_get_routes_caches(tmp_project):
    parser = FastAPIParser(str(tmp_project))
    first = parser.get_routes()
    second = parser.get_routes()
    assert first is second


def test_clear_cache(tmp_project):
    parser = FastAPIParser(str(tmp_project))
    first = parser.get_routes()
    parser.clear()
    assert parser._routes == []


def test_syntax_error_skipped(tmp_project):
    bad_file = tmp_project / "broken.py"
    bad_file.write_text("def (broken syntax:::")
    parser = FastAPIParser(str(tmp_project))
    routes = parser.parse()  # should not raise
    assert isinstance(routes, list)
