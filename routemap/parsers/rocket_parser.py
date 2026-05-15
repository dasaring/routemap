import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


ROCKET_ROUTE_PATTERN = re.compile(
    r'#\[(?P<method>get|post|put|delete|patch|head|options)\s*\(\s*"(?P<path>[^"]+)"',
    re.IGNORECASE,
)

ROCKET_IMPORT_PATTERN = re.compile(r'use\s+rocket(?:::|\s*;)')


class RocketParser(BaseParser):
    """Parser for Rust Rocket web framework route files."""

    name = "rocket"
    language = "Rust"

    def supports_file(self, path: Path) -> bool:
        if path.suffix != ".rs":
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return bool(ROCKET_IMPORT_PATTERN.search(content))
        except OSError:
            return False

    def parse(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        if not path.is_dir():
            routes.extend(self._parse_file(path))
        else:
            for rs_file in sorted(path.rglob("*.rs")):
                if self.supports_file(rs_file):
                    routes.extend(self._parse_file(rs_file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return routes

        for match in ROCKET_ROUTE_PATTERN.finditer(content):
            method = match.group("method").upper()
            route_path = match.group("path")
            routes.append(
                RouteEntry(
                    method=method,
                    path=route_path,
                    source=str(path),
                )
            )
        return routes
