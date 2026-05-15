import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


SINATRA_ROUTE_RE = re.compile(
    r'^\s*(get|post|put|patch|delete|options|head)\s+[\'"]([^\'"]+)[\'"]',
    re.IGNORECASE | re.MULTILINE,
)

SINATRA_INDICATORS = [
    r'require\s+[\'"]sinatra',
    r'Sinatra::Base',
    r'Sinatra::Application',
]


class SinatraParser(BaseParser):
    """Parser for Ruby Sinatra applications."""

    name = "sinatra"

    def supports_file(self, path: Path) -> bool:
        if path.suffix != ".rb":
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return False
        return any(re.search(pat, content) for pat in SINATRA_INDICATORS)

    def parse(self, root: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        for rb_file in root.rglob("*.rb"):
            if self.supports_file(rb_file):
                routes.extend(self._parse_file(rb_file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return routes
        for match in SINATRA_ROUTE_RE.finditer(content):
            method = match.group(1).upper()
            route_path = match.group(2)
            routes.append(
                RouteEntry(
                    method=method,
                    path=route_path,
                    source=str(path),
                )
            )
        return routes
