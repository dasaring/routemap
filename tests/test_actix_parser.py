import pytest
from pathlib import Path
from routemap.parsers.actix_parser import ActixParser


ACTIX_SOURCE = """
use actix_web::{web, App, HttpServer, HttpResponse, Responder};

#[get("/users")]
async fn list_users() -> impl Responder {
    HttpResponse::Ok().body("list")
}

#[post("/users")]
async fn create_user() -> impl Responder {
    HttpResponse::Created().body("created")
}

#[get("/users/{id}")]
async fn get_user() -> impl Responder {
    HttpResponse::Ok().body("user")
}

#[delete("/users/{id}")]
async fn delete_user() -> impl Responder {
    HttpResponse::Ok().body("deleted")
}

pub fn config(cfg: &mut web::ServiceConfig) {
    cfg.route("/health", web::get());
}
"""


@pytest.fixture
def tmp_actix_file(tmp_path):
    f = tmp_path / "main.rs"
    f.write_text(ACTIX_SOURCE)
    return f


@pytest.fixture
def parser():
    return ActixParser()


@pytest.fixture
def routes(parser, tmp_actix_file):
    return parser.parse(tmp_actix_file.parent)


def test_parser_supports_rs_with_actix_web(parser, tmp_actix_file):
    assert parser.supports_file(tmp_actix_file)


def test_parser_does_not_support_plain_rs(parser, tmp_path):
    f = tmp_path / "lib.rs"
    f.write_text("fn main() {}")
    assert not parser.supports_file(f)


def test_parser_does_not_support_python(parser, tmp_path):
    f = tmp_path / "main.py"
    f.write_text("import actix_web")
    assert not parser.supports_file(f)


def test_parser_finds_routes(routes):
    assert len(routes) >= 4


def test_parser_finds_all_methods(routes):
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "DELETE" in methods


def test_parser_finds_all_paths(routes):
    paths = {r.path for r in routes}
    assert "/users" in paths
    assert "/users/{id}" in paths


def test_route_source_is_set(routes, tmp_actix_file):
    for route in routes:
        assert route.source == str(tmp_actix_file)


def test_route_entry_repr(routes):
    for route in routes:
        assert route.method in repr(route)
        assert route.path in repr(route)


def test_parser_dot_route_style(parser, tmp_path):
    f = tmp_path / "server.rs"
    f.write_text(
        'use actix_web::{web};\n'
        'cfg.route("/health", web::get());\n'
        'cfg.route("/ping", web::post());\n'
    )
    found = parser.parse(tmp_path)
    paths = {r.path for r in found}
    assert "/health" in paths
    assert "/ping" in paths
