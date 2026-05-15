import pytest
from pathlib import Path
from routemap.parsers.nuxt_parser import NuxtParser


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "nuxt_app"


@pytest.fixture
def parser():
    return NuxtParser()


# --- supports_file ---

def test_parser_supports_server_api_ts(parser, tmp_path):
    f = tmp_path / "server" / "api" / "users.ts"
    f.parent.mkdir(parents=True)
    f.touch()
    assert parser.supports_file(f)


def test_parser_supports_server_api_js(parser, tmp_path):
    f = tmp_path / "server" / "api" / "health.js"
    f.parent.mkdir(parents=True)
    f.touch()
    assert parser.supports_file(f)


def test_parser_supports_pages_vue(parser, tmp_path):
    f = tmp_path / "pages" / "index.vue"
    f.parent.mkdir(parents=True)
    f.touch()
    assert parser.supports_file(f)


def test_parser_supports_pages_ts(parser, tmp_path):
    f = tmp_path / "pages" / "about.ts"
    f.parent.mkdir(parents=True)
    f.touch()
    assert parser.supports_file(f)


def test_parser_does_not_support_plain_js(parser, tmp_path):
    f = tmp_path / "utils" / "helpers.js"
    f.parent.mkdir(parents=True)
    f.touch()
    assert not parser.supports_file(f)


def test_parser_does_not_support_python(parser, tmp_path):
    f = tmp_path / "server" / "api" / "app.py"
    f.parent.mkdir(parents=True)
    f.touch()
    assert not parser.supports_file(f)


# --- API route parsing ---

def test_api_route_method_from_stem(parser, tmp_path):
    api_dir = tmp_path / "server" / "api" / "users"
    api_dir.mkdir(parents=True)
    f = api_dir / "index.post.ts"
    f.write_text("export default defineEventHandler(async (event) => {});")
    routes = parser.parse(tmp_path)
    assert any(r.method == "POST" for r in routes)


def test_api_route_path_derived_correctly(parser, tmp_path):
    api_dir = tmp_path / "server" / "api" / "users"
    api_dir.mkdir(parents=True)
    f = api_dir / "index.get.ts"
    f.write_text("export default defineEventHandler(async (event) => {});")
    routes = parser.parse(tmp_path)
    assert any("/api/users" in r.path for r in routes)


def test_api_route_dynamic_segment(parser, tmp_path):
    api_dir = tmp_path / "server" / "api" / "users"
    api_dir.mkdir(parents=True)
    f = api_dir / "[id].get.ts"
    f.write_text("export default defineEventHandler(async (event) => {});")
    routes = parser.parse(tmp_path)
    assert any(":id" in r.path for r in routes)


def test_api_route_defaults_to_get(parser, tmp_path):
    api_dir = tmp_path / "server" / "api"
    api_dir.mkdir(parents=True)
    f = api_dir / "health.ts"
    f.write_text("export default defineEventHandler(() => ({ status: 'ok' }));")
    routes = parser.parse(tmp_path)
    assert any(r.method == "GET" for r in routes)


# --- Page route parsing ---

def test_page_route_index(parser, tmp_path):
    pages_dir = tmp_path / "pages"
    pages_dir.mkdir()
    (pages_dir / "index.vue").write_text("<template><div>Home</div></template>")
    routes = parser.parse(tmp_path)
    assert any(r.path == "/" or r.path == "" for r in routes)


def test_page_route_nested(parser, tmp_path):
    pages_dir = tmp_path / "pages" / "users"
    pages_dir.mkdir(parents=True)
    (pages_dir / "profile.vue").write_text("<template><div>Profile</div></template>")
    routes = parser.parse(tmp_path)
    assert any("/users/profile" in r.path for r in routes)


def test_page_route_dynamic(parser, tmp_path):
    pages_dir = tmp_path / "pages" / "users"
    pages_dir.mkdir(parents=True)
    (pages_dir / "[id].vue").write_text("<template><div>User</div></template>")
    routes = parser.parse(tmp_path)
    assert any(":id" in r.path for r in routes)


def test_page_route_method_is_get(parser, tmp_path):
    pages_dir = tmp_path / "pages"
    pages_dir.mkdir()
    (pages_dir / "about.vue").write_text("<template><div>About</div></template>")
    routes = parser.parse(tmp_path)
    assert all(r.method == "GET" for r in routes)


# --- fixture-based ---

def test_fixture_route_found(parser):
    if not FIXTURE_DIR.exists():
        pytest.skip("Nuxt fixture directory not present")
    routes = parser.parse(FIXTURE_DIR)
    assert len(routes) > 0


def test_fixture_route_source_set(parser):
    if not FIXTURE_DIR.exists():
        pytest.skip("Nuxt fixture directory not present")
    routes = parser.parse(FIXTURE_DIR)
    assert all(r.source for r in routes)
