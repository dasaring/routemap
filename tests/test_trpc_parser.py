import pytest
from pathlib import Path
from routemap.parsers.trpc_parser import TRPCParser


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "trpc_app"


@pytest.fixture
def parser():
    return TRPCParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR / "server" / "router.ts")


def test_parser_supports_trpc_ts(parser, tmp_path):
    f = tmp_path / "router.ts"
    f.write_text("import { initTRPC } from '@trpc/server';\n")
    assert parser.supports_file(f)


def test_parser_supports_trpc_js(parser, tmp_path):
    f = tmp_path / "router.js"
    f.write_text("const trpc = require('@trpc/server');\n")
    assert parser.supports_file(f)


def test_parser_does_not_support_plain_ts(parser, tmp_path):
    f = tmp_path / "utils.ts"
    f.write_text("export const add = (a: number, b: number) => a + b;\n")
    assert not parser.supports_file(f)


def test_parser_does_not_support_python(parser, tmp_path):
    f = tmp_path / "app.py"
    f.write_text("from fastapi import FastAPI\n")
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_procedures(routes):
    names = {r.path for r in routes}
    assert "/trpc/listUsers" in names
    assert "/trpc/getUser" in names
    assert "/trpc/createUser" in names
    assert "/trpc/updateUser" in names
    assert "/trpc/deleteUser" in names
    assert "/trpc/onUserUpdate" in names


def test_query_maps_to_get(routes):
    list_route = next(r for r in routes if r.path == "/trpc/listUsers")
    assert list_route.method == "GET"


def test_mutation_maps_to_post(routes):
    create_route = next(r for r in routes if r.path == "/trpc/createUser")
    assert create_route.method == "POST"


def test_subscription_maps_to_ws(routes):
    sub_route = next(r for r in routes if r.path == "/trpc/onUserUpdate")
    assert sub_route.method == "WS"


def test_source_is_file_path(routes):
    for route in routes:
        assert "router.ts" in route.source


def test_parse_directory(parser, tmp_path):
    router_file = tmp_path / "router.ts"
    router_file.write_text(
        "import { initTRPC } from '@trpc/server';\n"
        "const t = initTRPC.create();\n"
        "export const r = t.router({ health: t.procedure.query(async () => 'ok') });\n"
    )
    routes = parser.parse(tmp_path)
    assert any(r.path == "/trpc/health" for r in routes)
