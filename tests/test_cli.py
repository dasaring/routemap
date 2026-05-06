"""Tests for the routemap CLI."""

import textwrap
from pathlib import Path

import pytest

from routemap.cli import run


@pytest.fixture()
def fastapi_file(tmp_path: Path) -> Path:
    src = textwrap.dedent("""
        from fastapi import FastAPI
        app = FastAPI()

        @app.get("/items")
        def list_items():
            return []

        @app.post("/items")
        def create_item():
            return {}

        @app.delete("/items/{item_id}")
        def delete_item(item_id: int):
            return {}
    """)
    f = tmp_path / "main.py"
    f.write_text(src)
    return f


@pytest.fixture()
def express_file(tmp_path: Path) -> Path:
    src = textwrap.dedent("""
        const express = require('express');
        const router = express.Router();
        router.get('/users', (req, res) => res.json([]));
        router.post('/users', (req, res) => res.json({}));
        module.exports = router;
    """)
    f = tmp_path / "users.js"
    f.write_text(src)
    return f


def test_run_with_fastapi_file_returns_zero(fastapi_file: Path) -> None:
    assert run([str(fastapi_file)]) == 0


def test_run_with_express_file_returns_zero(express_file: Path) -> None:
    assert run([str(express_file)]) == 0


def test_run_nonexistent_path_returns_one(tmp_path: Path) -> None:
    assert run([str(tmp_path / "nonexistent")]) == 1


def test_run_mermaid_renderer(fastapi_file: Path, capsys: pytest.CaptureFixture) -> None:
    rc = run([str(fastapi_file), "--renderer", "mermaid"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "graph" in captured.out


def test_run_ascii_no_color(fastapi_file: Path, capsys: pytest.CaptureFixture) -> None:
    rc = run([str(fastapi_file), "--no-color"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "/items" in captured.out


def test_run_writes_output_file(fastapi_file: Path, tmp_path: Path) -> None:
    out_file = tmp_path / "routes.txt"
    rc = run([str(fastapi_file), "--output", str(out_file)])
    assert rc == 0
    assert out_file.exists()
    assert "/items" in out_file.read_text()


def test_run_directory_scans_all_files(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    (tmp_path / "a.py").write_text(
        "from fastapi import FastAPI\napp=FastAPI()\n@app.get('/ping')\ndef ping(): pass\n"
    )
    (tmp_path / "b.js").write_text(
        "const r=require('express').Router();r.get('/health',(q,s)=>s.json({}));module.exports=r;\n"
    )
    rc = run([str(tmp_path)])
    assert rc == 0
    captured = capsys.readouterr()
    assert "/ping" in captured.out
    assert "/health" in captured.out
