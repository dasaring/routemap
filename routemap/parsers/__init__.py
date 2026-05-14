from pathlib import Path
from typing import Optional, List

from .base import BaseParser
from .fastapi_parser import FastAPIParser
from .express_parser import ExpressParser
from .django_parser import DjangoParser
from .flask_parser import FlaskParser
from .rails_parser import RailsParser
from .spring_parser import SpringParser
from .gin_parser import GinParser
from .laravel_parser import LaravelParser
from .nestjs_parser import NestJSParser
from .koa_parser import KoaParser
from .hapi_parser import HapiParser
from .fastify_parser import FastifyParser
from .fiber_parser import FiberParser
from .actix_parser import ActixParser
from .phoenix_parser import PhoenixParser
from .dotnet_parser import DotNetParser
from .asp_parser import AspParser
from .aiohttp_parser import AiohttpParser
from .tornado_parser import TornadoParser
from .sanic_parser import SanicParser
from .grape_parser import GrapeParser

_REGISTRY = {
    'fastapi': FastAPIParser,
    'express': ExpressParser,
    'django': DjangoParser,
    'flask': FlaskParser,
    'rails': RailsParser,
    'spring': SpringParser,
    'gin': GinParser,
    'laravel': LaravelParser,
    'nestjs': NestJSParser,
    'koa': KoaParser,
    'hapi': HapiParser,
    'fastify': FastifyParser,
    'fiber': FiberParser,
    'actix': ActixParser,
    'phoenix': PhoenixParser,
    'dotnet': DotNetParser,
    'asp': AspParser,
    'aiohttp': AiohttpParser,
    'tornado': TornadoParser,
    'sanic': SanicParser,
    'grape': GrapeParser,
}


def get_parser(name: str) -> Optional[BaseParser]:
    """Return a parser instance by framework name (case-insensitive)."""
    cls = _REGISTRY.get(name.lower())
    return cls() if cls else None


def detect_parser(path: Path) -> Optional[BaseParser]:
    """Auto-detect and return the appropriate parser for a given file."""
    for cls in _REGISTRY.values():
        instance = cls()
        if instance.supports_file(path):
            return instance
    return None


def available_parsers() -> List[str]:
    """Return a list of all registered parser names."""
    return list(_REGISTRY.keys())
