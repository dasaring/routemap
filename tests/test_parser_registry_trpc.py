import pytest
from pathlib import Path
from routemap.parsers import get_parser, detect_parser, available_parsers


def test_get_parser_trpc():
    parser = get_parser("trpc")
    assert parser is not None
    assert parser.__class__.__name__ == "TRPCParser"


def test_get_parser_trpc_case_insensitive():
    assert get_parser("TRPC") is not None
    assert get_parser("Trpc") is not None


def test_trpc_in_available_parsers():
    parsers = available_parsers()
    assert "trpc" in parsers


def test_detect_parser_trpc_ts(tmp_path):
    f = tmp_path / "router.ts"
    f.write_text("import { initTRPC } from '@trpc/server';\n")
    parser = detect_parser(f)
    assert parser is not None
    assert parser.__class__.__name__ == "TRPCParser"


def test_detect_parser_does_not_match_plain_ts(tmp_path):
    f = tmp_path / "utils.ts"
    f.write_text("export const x = 1;\n")
    parser = detect_parser(f)
    assert parser is None or parser.__class__.__name__ != "TRPCParser"
