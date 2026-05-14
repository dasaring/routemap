import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


class TornadoParser(BaseParser):
    """Parser for Tornado web framework Python files."""

    # Matches: (r"/path", HandlerClass) or (r'/path', HandlerClass)
    _ROUTE_PATTERN = re.compile(
        r'\(\s*r?["\']([^"\']+)["\']\s*,\s*(\w+)\s*\)'
    )

    # Matches HTTP method definitions inside handler classes
    _METHOD_PATTERN = re.compile(
        r'^\s*(?:async\s+)?def\s+(get|post|put|patch|delete|head|options)\s*\(',
        re.MULTILINE | re.IGNORECASE,
    )

    _TORNADO_IMPORT = re.compile(r'import tornado|from tornado')

    def supports_file(self, path: Path) -> bool:
        if path.suffix != '.py':
            return False
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
            return bool(self._TORNADO_IMPORT.search(content))
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
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            return []

        if not self._TORNADO_IMPORT.search(content):
            return []

        routes: List[RouteEntry] = []
        url_patterns = self._ROUTE_PATTERN.findall(content)

        # Collect methods defined in handler classes
        methods_found = [
            m.upper() for m in self._METHOD_PATTERN.findall(content)
        ]
        if not methods_found:
            methods_found = ['GET']

        for url_path, _handler in url_patterns:
            for method in methods_found:
                routes.append(
                    RouteEntry(
                        method=method,
                        path=url_path,
                        source=str(path),
                    )
                )

        return routes
