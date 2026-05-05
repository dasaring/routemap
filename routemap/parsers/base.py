"""Base parser interface for route extraction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RouteEntry:
    """Represents a single API route extracted from source code."""

    method: str
    path: str
    handler: str
    file: str
    line: int
    tags: list[str] = field(default_factory=list)
    summary: Optional[str] = None

    def __post_init__(self):
        self.method = self.method.upper()

    def __repr__(self) -> str:
        return f"RouteEntry({self.method} {self.path} -> {self.handler})"


class BaseParser(ABC):
    """Abstract base class for framework-specific route parsers."""

    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self._routes: list[RouteEntry] = []

    @abstractmethod
    def parse(self) -> list[RouteEntry]:
        """Parse source files and return extracted route entries."""
        ...

    @abstractmethod
    def supports_file(self, filename: str) -> bool:
        """Return True if this parser can handle the given file."""
        ...

    def get_routes(self) -> list[RouteEntry]:
        """Return cached routes, parsing if necessary."""
        if not self._routes:
            self._routes = self.parse()
        return self._routes

    def clear(self) -> None:
        """Clear cached routes."""
        self._routes = []
