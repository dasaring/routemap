import pytest
from pathlib import Path
from routemap.parsers import get_parser, detect_parser, available_parsers
from routemap.parsers.fastify_ts_parser import FastifyTSParser


def test_get_parser_fastify_ts():
    parser = get_parser("fastify_ts")
    assert parser is not None
    assert isinstance(parser, FastifyTSParser)


def test_get_parser_fastify_ts_case_insensitive():
    assert get_parser("Fastify_TS") is not None
    assert get_parser("FASTIFY_TS") is not None
    assert get_parser("fastify_ts") is not None


def test_fastify_ts_in_available_parsers():
    parsers = available_parsers()
    assert "fastify_ts" in parsers


def test_detect_parser_fastify_ts_file(tmp_path):
    f = tmp_path / "server.ts"
    f.write_text(
        "import { FastifyInstance } from 'fastify';\n"
        "const app: FastifyInstance = fastify();\n"
        "app.get('/hello', handler);\n"
    )
    parser = detect_parser(f)
    assert parser is not None
    assert isinstance(parser, FastifyTSParser)


def test_detect_parser_does_not_match_plain_ts(tmp_path):
    f = tmp_path / "utils.ts"
    f.write_text("export const greet = (name: string) => `Hello, ${name}!`;")
    parser = detect_parser(f)
    # Should not detect as FastifyTS
    assert not isinstance(parser, FastifyTSParser)
