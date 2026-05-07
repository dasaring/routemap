import pytest
from pathlib import Path
from routemap.parsers.flask_parser import FlaskParser

FIXTURE_PATH = Path(__file__).parent / 'fixtures' / 'flask_app' / 'app.py'


@pytest.fixture
def parser():
    return FlaskParser()


@pytest.fixture
def routes(parser):
    return parser.parse(FIXTURE_PATH)


def test_parser_supports_flask_py(parser):
    assert parser.supports_file(FIXTURE_PATH) is True


def test_parser_does_not_support_js(parser, tmp_path):
    js_file = tmp_path / 'app.js'
    js_file.write_text('app.get("/", handler)')
    assert parser.supports_file(js_file) is False


def test_parser_does_not_support_plain_py(parser, tmp_path):
    py_file = tmp_path / 'utils.py'
    py_file.write_text('def helper(): pass')
    assert parser.supports_file(py_file) is False


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_paths(routes):
    paths = {r.path for r in routes}
    assert '/users' in paths
    assert '/users/<int:user_id>' in paths
    assert '/health' in paths


def test_parser_finds_all_methods(routes):
    methods = {r.method for r in routes}
    assert 'GET' in methods
    assert 'POST' in methods
    assert 'DELETE' in methods


def test_put_and_patch_methods(routes):
    update_routes = [r for r in routes if r.path == '/users/<int:user_id>']
    methods = {r.method for r in update_routes}
    assert 'PUT' in methods
    assert 'PATCH' in methods


def test_default_method_is_get(routes):
    health_routes = [r for r in routes if r.path == '/health']
    assert len(health_routes) == 1
    assert health_routes[0].method == 'GET'


def test_route_handler_names(routes):
    handlers = {r.handler for r in routes}
    assert 'list_users' in handlers
    assert 'create_user' in handlers
    assert 'delete_user' in handlers
    assert 'health_check' in handlers


def test_route_source_is_set(routes):
    for route in routes:
        assert route.source is not None
        assert 'app.py' in route.source


def test_parse_directory(parser, tmp_path):
    app_file = tmp_path / 'app.py'
    app_file.write_text(
        'from flask import Flask\napp = Flask(__name__)\n'
        '@app.route("/ping")\ndef ping(): return "pong"\n'
    )
    routes = parser.parse(tmp_path)
    assert any(r.path == '/ping' for r in routes)
