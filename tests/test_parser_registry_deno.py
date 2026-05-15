import pytest
from pathlib import Path
from routemap.parsers import get_parser, detect_parser, available_parsers
from routemap.parsers.deno_parser import DenoParser


def test_get_parser_deno():
    parser = get_parser("deno")
    assert isinstance(parser, DenoParser)


def test_get_parser_deno_case_insensitive():
    assert isinstance(get_parser("Deno"), DenoParser)
    assert isinstance(get_parser("DENO"), DenoParser)


def test_deno_in_available_parsers():
    parsers = available_parsers()
    assert "deno" in parsers


def test_detect_parser_deno_ts(tmp_path):
    f = tmp_path / "server.ts"
    f.write_text(
        'import { Router } from "https://deno.land/x/oak/mod.ts";\n'
        'router.get("/", handler);\n'
    )
    parser = detect_parser(f)
    assert isinstance(parser, DenoParser)


def test_detect_parser_does_not_match_plain_ts(tmp_path):
    f = tmp_path / "utils.ts"
    f.write_text("export const add = (a: number, b: number) => a + b;")
    parser = detect_parser(f)
    assert not isinstance(parser, DenoParser)
