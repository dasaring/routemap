from pathlib import Path
from typing import Optional, Dict, List

from routemap.parsers.base import BaseParser
from routemap.parsers.fastapi_parser import FastAPIParser
from routemap.parsers.express_parser import ExpressParser
from routemap.parsers.django_parser import DjangoParser
from routemap.parsers.flask_parser import FlaskParser
from routemap.parsers.rails_parser import RailsParser
from routemap.parsers.spring_parser import SpringParser
from routemap.parsers.gin_parser import GinParser
from routemap.parsers.laravel_parser import LaravelParser
from routemap.parsers.nestjs_parser import NestJSParser
from routemap.parsers.koa_parser import KoaParser
from routemap.parsers.hapi_parser import HapiParser
from routemap.parsers.fastify_parser import FastifyParser
from routemap.parsers.fiber_parser import FiberParser
from routemap.parsers.actix_parser import ActixParser
from routemap.parsers.phoenix_parser import PhoenixParser

_REGISTRY: Dict[str, BaseParser] = {
    "fastapi": FastAPIParser(),
    "express": ExpressParser(),
    "django": DjangoParser(),
    "flask": FlaskParser(),
    "rails": RailsParser(),
    "spring": SpringParser(),
    "gin": GinParser(),
    "laravel": LaravelParser(),
    "nestjs": NestJSParser(),
    "koa": KoaParser(),
    "hapi": HapiParser(),
    "fastify": FastifyParser(),
    "fiber": FiberParser(),
    "actix": ActixParser(),
    "phoenix": PhoenixParser(),
}


def get_parser(name: str) -> Optional[BaseParser]:
    """Return a parser instance by framework name (case-insensitive)."""
    return _REGISTRY.get(name.lower())


def detect_parser(path: Path) -> Optional[BaseParser]:
    """Auto-detect a suitable parser for the given file path."""
    for parser in _REGISTRY.values():
        if parser.supports_file(path):
            return parser
    return None


def available_parsers() -> List[str]:
    """Return a sorted list of registered parser names."""
    return sorted(_REGISTRY.keys())
