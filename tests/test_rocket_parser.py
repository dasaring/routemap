import pytest
from pathlib import Path
from routemap.parsers.rocket_parser import RocketParser

FIXTURE_DIR = Path("tests/fixtures/rocket_app/src")


@pytest.fixture
def parser():
    return RocketParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR)


def test_parser_supports_rs_with_rocket(parser, tmp_path):
    f = tmp_path / "main.rs"
    f.write_text('use rocket;\n#[get("/")]\nfn index() {}')
    assert parser.supports_file(f)


def test_parser_does_not_support_plain_rs(parser, tmp_path):
    f = tmp_path / "lib.rs"
    f.write_text("fn main() {}")
    assert not parser.supports_file(f)


def test_parser_does_not_support_python(parser, tmp_path):
    f = tmp_path / "app.py"
    f.write_text("import rocket")
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "PUT" in methods
    assert "DELETE" in methods


def test_parser_finds_list_users(routes):
    paths = [r.path for r in routes]
    assert "/users" in paths


def test_parser_finds_parameterized_route(routes):
    paths = [r.path for r in routes]
    assert any("<id>" in p for p in paths)


def test_parser_finds_health(routes):
    paths = [r.path for r in routes]
    assert "/health" in paths


def test_route_source_is_set(routes):
    for route in routes:
        assert route.source is not None
        assert route.source.endswith(".rs")


def test_parser_route_count(routes):
    assert len(routes) == 6
