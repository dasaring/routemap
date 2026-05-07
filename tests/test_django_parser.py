import pytest
from pathlib import Path
from routemap.parsers.django_parser import DjangoParser


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "django_app"


@pytest.fixture
def parser():
    return DjangoParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR)


def test_parser_supports_urls_py(parser):
    assert parser.supports_file(Path("myapp/urls.py"))


def test_parser_does_not_support_views(parser):
    assert not parser.supports_file(Path("myapp/views.py"))


def test_parser_does_not_support_js(parser):
    assert not parser.supports_file(Path("app.js"))


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_user_list(routes):
    paths = [r.path for r in routes]
    assert "/users/" in paths


def test_parser_finds_legacy_endpoint(routes):
    paths = [r.path for r in routes]
    assert "/legacy/items/" in paths


def test_router_generates_crud_routes(routes):
    product_routes = [r for r in routes if "products" in r.path]
    methods = {r.method for r in product_routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "DELETE" in methods


def test_all_routes_have_method(routes):
    for route in routes:
        assert route.method in {"GET", "POST", "PUT", "PATCH", "DELETE"}


def test_all_routes_have_source_file(routes):
    for route in routes:
        assert route.source_file.endswith(".py")


def test_router_prefix_has_id_variant(routes):
    product_detail = [r for r in routes if r.path == "/products/{id}"]
    assert len(product_detail) > 0
