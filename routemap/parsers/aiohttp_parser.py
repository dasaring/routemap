import re
from pathlib import Path
from typing import List
from .base import BaseParser, RouteEntry


class AiohttpParser(BaseParser):
    """Parser for aiohttp web applications."""

    # Matches: app.router.add_get('/path', handler)
    # or: app.router.add_route('GET', '/path', handler)
    _ROUTE_PATTERN = re.compile(
        r'(?:app|router)\.(?:router\.)?add_(?P<shortmethod>get|post|put|patch|delete|head|options)'
        r"\(\s*['\"](?P<path>[^'\"]+)['\"]",
        re.IGNORECASE,
    )
    _ROUTE_GENERIC_PATTERN = re.compile(
        r'(?:app|router)\.(?:router\.)?add_route\(\s*['\"](?P<method>[A-Z]+)['\"]\s*,\s*['\"](?P<path>[^'\"]+)['\"]',
        re.IGNORECASE,
    )
    _AIOHTTP_IMPORT = re.compile(r'(?:from\s+aiohttp|import\s+aiohttp)')

    def supports_file(self, path: Path) -> bool:
        if path.suffix not in ('.py',):
            return False
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
            return bool(self._AIOHTTP_IMPORT.search(content))
        except OSError:
            return False

    def parse(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        if path.is_file():
            routes.extend(self._parse_file(path))
        elif path.is_dir():
            for py_file in sorted(path.rglob('*.py')):
                if self.supports_file(py_file):
                    routes.extend(self._parse_file(py_file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            return routes

        for match in self._ROUTE_PATTERN.finditer(content):
            method = match.group('shortmethod').upper()
            route_path = match.group('path')
            line_no = content[: match.start()].count('\n') + 1
            routes.append(
                RouteEntry(
                    method=method,
                    path=route_path,
                    source=str(path),
                    line=line_no,
                )
            )

        for match in self._ROUTE_GENERIC_PATTERN.finditer(content):
            method = match.group('method').upper()
            route_path = match.group('path')
            line_no = content[: match.start()].count('\n') + 1
            routes.append(
                RouteEntry(
                    method=method,
                    path=route_path,
                    source=str(path),
                    line=line_no,
                )
            )

        return routes
