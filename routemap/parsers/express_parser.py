import re
from pathlib import Path
from typing import List

from routemap.parsers.base import BaseParser, RouteEntry

# Matches: router.get('/path', ...) or app.post('/path', ...)
ROUTE_PATTERN = re.compile(
    r'(?:router|app)\.(get|post|put|patch|delete|options|head)\s*\(\s*[\'"]([^\'"]+)[\'"]',
    re.IGNORECASE,
)

# Matches: router.route('/path').get(...).post(...)
CHAINED_ROUTE_PATTERN = re.compile(
    r'(?:router|app)\.route\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)([^;]+)',
    re.IGNORECASE | re.DOTALL,
)

CHAINED_METHOD_PATTERN = re.compile(r'\.(get|post|put|patch|delete|options|head)\s*\(', re.IGNORECASE)


class ExpressParser(BaseParser):
    """Parser for Express.js route definitions."""

    SUPPORTED_EXTENSIONS = {".js", ".ts", ".mjs", ".cjs"}

    def supports_file(self, path: Path) -> bool:
        return path.suffix in self.SUPPORTED_EXTENSIONS

    def parse(self, root: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        for file_path in root.rglob("*"):
            if file_path.is_file() and self.supports_file(file_path):
                routes.extend(self._parse_file(file_path))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return routes

        for match in ROUTE_PATTERN.finditer(source):
            method, route_path = match.group(1).upper(), match.group(2)
            line_number = source[: match.start()].count("\n") + 1
            routes.append(
                RouteEntry(
                    method=method,
                    path=route_path,
                    source_file=str(path),
                    line_number=line_number,
                )
            )

        for match in CHAINED_ROUTE_PATTERN.finditer(source):
            route_path = match.group(1)
            chain_body = match.group(2)
            line_number = source[: match.start()].count("\n") + 1
            for method_match in CHAINED_METHOD_PATTERN.finditer(chain_body):
                routes.append(
                    RouteEntry(
                        method=method_match.group(1).upper(),
                        path=route_path,
                        source_file=str(path),
                        line_number=line_number,
                    )
                )

        return routes
