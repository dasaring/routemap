import pytest
from pathlib import Path
from routemap.parsers import get_parser, detect_parser, available_parsers
from routemap.parsers.spring_parser import SpringParser


def test_get_parser_spring():
    parser = get_parser("spring")
    assert isinstance(parser, SpringParser)


def test_get_parser_spring_case_insensitive():
    assert isinstance(get_parser("Spring"), SpringParser)
    assert isinstance(get_parser("SPRING"), SpringParser)


def test_spring_in_available_parsers():
    assert "spring" in available_parsers()


def test_detect_parser_java_file():
    parser = detect_parser(Path("UserController.java"))
    assert isinstance(parser, SpringParser)


def test_detect_parser_kotlin_file():
    parser = detect_parser(Path("UserController.kt"))
    assert isinstance(parser, SpringParser)


def test_detect_parser_does_not_match_py():
    parser = detect_parser(Path("app.py"))
    assert not isinstance(parser, SpringParser)
