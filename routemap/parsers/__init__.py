"""Route parsers for supported frameworks."""

from routemap.parsers.base import BaseParser, RouteEntry
from routemap.parsers.fastapi_parser import FastAPIParser
from routemap.parsers.express_parser import ExpressParser

__all__ = [
    "BaseParser",
    "RouteEntry",
    "FastAPIParser",
    "ExpressParser",
]

PARSER_REGISTRY: dict[str, type[BaseParser]] = {
    "fastapi": FastAPIParser,
    "express": ExpressParser,
}


def get_parser(framework: str) -> BaseParser:
    """Instantiate a parser by framework name.

    Args:
        framework: One of 'fastapi' or 'express'.

    Returns:
        An instance of the corresponding parser.

    Raises:
        ValueError: If the framework is not supported.
    """
    key = framework.lower().strip()
    if key not in PARSER_REGISTRY:
        supported = ", ".join(sorted(PARSER_REGISTRY))
        raise ValueError(f"Unsupported framework '{framework}'. Choose from: {supported}")
    return PARSER_REGISTRY[key]()
