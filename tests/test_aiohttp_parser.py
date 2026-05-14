import pytest
from pathlib import Path
from routemap.parsers.aiohttp_parser import AiohttpParser

FIXTURE_DIR = Path(__file__).parent / 'fixtures' / 'aiohttp_app'


@pytest.fixture
def parser():
    return AiohttpParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_DIR / 'app.py')


def test_parser_supports_aiohttp_py(parser, tmp_path):
    f = tmp_path / 'app.py'
    f.write_text('from aiohttp import web\napp = web.Application()\n')
    assert parser.supports_file(f)


def test_parser_does_not_support_plain_py(parser, tmp_path):
    f = tmp_path / 'utils.py'
    f.write_text('def helper():\n    pass\n')
    assert not parser.supports_file(f)


def test_parser_does_not_support_js(parser, tmp_path):
    f = tmp_path / 'app.js'
    f.write_text('const aiohttp = require("aiohttp");\n')
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_routes(routes):
    assert len(routes) == 6


def test_parser_finds_get_users(routes):
    paths = [r.path for r in routes]
    assert '/users' in paths


def test_parser_finds_all_methods(routes):
    methods = {r.method for r in routes}
    assert 'GET' in methods
    assert 'POST' in methods
    assert 'PUT' in methods
    assert 'DELETE' in methods


def test_parser_finds_parameterized_paths(routes):
    paths = [r.path for r in routes]
    assert '/users/{id}' in paths


def test_parser_generic_add_route(routes):
    health_routes = [r for r in routes if r.path == '/health']
    assert len(health_routes) == 1
    assert health_routes[0].method == 'GET'


def test_route_source_is_set(routes):
    for route in routes:
        assert route.source is not None
        assert route.source.endswith('app.py')


def test_route_line_numbers(routes):
    for route in routes:
        assert route.line is not None
        assert route.line > 0


def test_parse_directory(parser, tmp_path):
    app_file = tmp_path / 'app.py'
    app_file.write_text(
        'import aiohttp\nfrom aiohttp import web\n'
        'app = web.Application()\n'
        'app.router.add_get("/ping", ping_handler)\n'
        'app.router.add_post("/items", create_item)\n'
    )
    found = parser.parse(tmp_path)
    assert len(found) == 2
    paths = [r.path for r in found]
    assert '/ping' in paths
    assert '/items' in paths
