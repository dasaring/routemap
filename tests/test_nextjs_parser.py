import pytest
from pathlib import Path
from routemap.parsers.nextjs_parser import NextJSParser


FIXTURES = Path(__file__).parent / "fixtures" / "nextjs_app"


@pytest.fixture
def parser():
    return NextJSParser()


# ── supports_file ────────────────────────────────────────────────────────────

def test_parser_supports_pages_api_js(parser):
    assert parser.supports_file("pages/api/users.js")


def test_parser_supports_pages_api_ts(parser):
    assert parser.supports_file("pages/api/items/[id].ts")


def test_parser_supports_app_route_ts(parser):
    assert parser.supports_file("app/users/route.ts")


def test_parser_supports_app_route_js(parser):
    assert parser.supports_file("app/products/[id]/route.js")


def test_parser_does_not_support_plain_ts(parser):
    assert not parser.supports_file("lib/utils.ts")


def test_parser_does_not_support_non_route_app_file(parser):
    assert not parser.supports_file("app/users/page.tsx")


def test_parser_does_not_support_js_outside_api(parser):
    assert not parser.supports_file("pages/index.js")


# ── route path derivation ─────────────────────────────────────────────────────

def test_derive_path_pages_api(parser, tmp_path):
    f = tmp_path / "pages" / "api" / "users.ts"
    f.parent.mkdir(parents=True)
    f.write_text("export default async function handler(req, res) {}")
    routes = parser._parse_file(f, tmp_path)
    assert all(r.path == "/users" for r in routes)


def test_derive_path_dynamic_segment(parser, tmp_path):
    f = tmp_path / "pages" / "api" / "users" / "[id].ts"
    f.parent.mkdir(parents=True)
    f.write_text("export default async function handler(req, res) {}")
    routes = parser._parse_file(f, tmp_path)
    assert all(r.path == "/users/:id" for r in routes)


def test_derive_path_app_router(parser, tmp_path):
    f = tmp_path / "app" / "products" / "[id]" / "route.ts"
    f.parent.mkdir(parents=True)
    f.write_text("export async function GET(req) {}\nexport async function DELETE(req) {}")
    routes = parser._parse_file(f, tmp_path)
    assert all(r.path == "/products/:id" for r in routes)


# ── method detection ──────────────────────────────────────────────────────────

def test_app_router_extracts_explicit_methods(parser, tmp_path):
    f = tmp_path / "app" / "items" / "route.ts"
    f.parent.mkdir(parents=True)
    f.write_text(
        "export async function GET(req) {}\n"
        "export async function POST(req) {}\n"
        "export async function DELETE(req) {}\n"
    )
    routes = parser._parse_file(f, tmp_path)
    methods = {r.method for r in routes}
    assert methods == {"GET", "POST", "DELETE"}


def test_pages_router_default_export_generates_all_methods(parser, tmp_path):
    f = tmp_path / "pages" / "api" / "ping.ts"
    f.parent.mkdir(parents=True)
    f.write_text("export default function handler(req, res) { res.json({ok: true}); }")
    routes = parser._parse_file(f, tmp_path)
    methods = {r.method for r in routes}
    assert {"GET", "POST", "PUT", "PATCH", "DELETE"}.issubset(methods)


# ── fixture-based integration ─────────────────────────────────────────────────

def test_parse_fixture_directory(parser):
    routes = parser.parse(str(FIXTURES))
    assert len(routes) > 0


def test_fixture_routes_have_dynamic_segment(parser):
    routes = parser.parse(str(FIXTURES))
    paths = [r.path for r in routes]
    assert any(":id" in p for p in paths)
