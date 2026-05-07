from pathlib import Path
from typing import Optional
from .base import BaseParser
from .fastapi_parser import FastAPIParser
from .express_parser import ExpressParser
from .django_parser import DjangoParser

_PARSERS = [
    FastAPIParser,
    ExpressParser,
    DjangoParser,
]


def get_parser(name: str) -> Optional[BaseParser]:
    """Return a parser instance by name.

    Supported names: 'fastapi', 'express', 'django'.
    Returns None if the name is not recognised.
    """
    mapping = {
        "fastapi": FastAPIParser,
        "express": ExpressParser,
        "django": DjangoParser,
    }
    cls = mapping.get(name.lower())
    return cls() if cls else None


def detect_parser(root: Path) -> Optional[BaseParser]:
    """Auto-detect the appropriate parser for a project directory.

    Heuristics:
      - presence of requirements.txt mentioning fastapi  -> FastAPIParser
      - presence of package.json / .js files             -> ExpressParser
      - presence of manage.py or django in requirements  -> DjangoParser
    """
    req = root / "requirements.txt"
    if req.exists():
        text = req.read_text(encoding="utf-8").lower()
        if "fastapi" in text:
            return FastAPIParser()
        if "django" in text:
            return DjangoParser()

    if (root / "package.json").exists() or list(root.rglob("*.js")):
        return ExpressParser()

    if (root / "manage.py").exists():
        return DjangoParser()

    return None


def available_parsers():
    """Return names of all registered parsers."""
    return ["fastapi", "express", "django"]
