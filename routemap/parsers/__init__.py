from typing import List, Optional, Type
from pathlib import Path

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
from routemap.parsers.dotnet_parser import DotNetParser
from routemap.parsers.asp_parser import AspParser
from routemap.parsers.aiohttp_parser import AiohttpParser
from routemap.parsers.tornado_parser import TornadoParser
from routemap.parsers.sanic_parser import SanicParser
from routemap.parsers.grape_parser import GrapeParser
from routemap.parsers.sinatra_parser import SinatraParser

_REGISTRY: List[Type[BaseParser]] = [
    FastAPIParser,
    ExpressParser,
    DjangoParser,
    FlaskParser,
    RailsParser,
    SpringParser,
    GinParser,
    LaravelParser,
    NestJSParser,
    KoaParser,
    HapiParser,
    FastifyParser,
    FiberParser,
    ActixParser,
    PhoenixParser,
    DotNetParser,
    AspParser,
    AiohttpParser,
    TornadoParser,
    SanicParser,
    GrapeParser,
    SinatraParser,
]


def get_parser(name: str) -> Optional[BaseParser]:
    """Return an instantiated parser by framework name (case-insensitive)."""
    name_lower = name.lower()
    for cls in _REGISTRY:
        if cls.name.lower() == name_lower:
            return cls()
    return None


def detect_parser(path: Path) -> Optional[BaseParser]:
    """Auto-detect a suitable parser for the given file path."""
    for cls in _REGISTRY:
        instance = cls()
        if instance.supports_file(path):
            return instance
    return None


def available_parsers() -> List[BaseParser]:
    """Return one instance of every registered parser."""
    return [cls() for cls in _REGISTRY]
