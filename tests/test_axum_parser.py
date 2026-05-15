import pytest
from pathlib import Path
from routemap.parsers.axum_parser import AxumParser


AXUM_SOURCE = """
use axum::{
    routing::{get, post, put, delete},
    Router,
};

async fn list_users() {}
async fn create_user() {}
async fn get_user() {}
async fn update_user() {}
async fn delete_user() {}
async fn health() {}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/users", get(list_users).post(create_user))
        .route("/users/:id", get(get_user).put(update_user).delete(delete_user))
        .route("/health", get(health));
}
"""


@pytest.fixture
def tmp_axum_file(tmp_path):
    f = tmp_path / "main.rs"
    f.write_text(AXUM_SOURCE)
    return f


@pytest.fixture
def parser():
    return AxumParser()


@pytest.fixture
def routes(parser, tmp_axum_file):
    return parser.parse(tmp_axum_file)


def test_parser_supports_rs_with_axum(parser, tmp_axum_file):
    assert parser.supports_file(tmp_axum_file)


def test_parser_does_not_support_plain_rs(parser, tmp_path):
    f = tmp_path / "lib.rs"
    f.write_text("fn main() {}\n")
    assert not parser.supports_file(f)


def test_parser_does_not_support_python(parser, tmp_path):
    f = tmp_path / "app.py"
    f.write_text("import axum\n")
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) > 0


def test_parser_finds_all_paths(routes):
    paths = {r.path for r in routes}
    assert "/users" in paths
    assert "/users/:id" in paths
    assert "/health" in paths


def test_parser_finds_get_method(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods


def test_parser_finds_post_method(routes):
    methods = {r.method for r in routes}
    assert "POST" in methods


def test_parser_finds_delete_method(routes):
    methods = {r.method for r in routes}
    assert "DELETE" in methods


def test_parser_sets_framework(routes):
    for route in routes:
        assert route.framework == "axum"


def test_parser_sets_source(routes, tmp_axum_file):
    for route in routes:
        assert route.source == str(tmp_axum_file)


def test_parser_parses_directory(parser, tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.rs").write_text(AXUM_SOURCE)
    found = parser.parse(tmp_path)
    assert any(r.path == "/health" for r in found)
