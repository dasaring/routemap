import re
from pathlib import Path
from typing import List
from .base import BaseParser, RouteEntry


class FastifyParser(BaseParser):
    """Parser for Fastify (Node.js) route definitions."""

    METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}

    # Matches: fastify.get('/path', ...) or app.get('/path', ...)
    ROUTE_RE = re.compile(
        r'(?:fastify|app|router|server)\.(get|post|put|patch|delete|head|options)'
        r'\s*\(\s*[\'"]([^\'"]+)[\'"]',
        re.IGNORECASE,
    )

    # Matches: fastify.route({ method: 'GET', url: '/path' })
    ROUTE_OBJ_METHOD_RE = re.compile(
        r'method\s*:\s*[\'"]([A-Z]+)[\'"]', re.IGNORECASE
    )
    ROUTE_OBJ_URL_RE = re.compile(
        r'url\s*:\s*[\'"]([^\'"]+)[\'"]'
    )
    ROUTE_OBJ_RE = re.compile(
        r'(?:fastify|app|router|server)\.route\s*\(\s*\{([^}]+)\}',
        re.DOTALL,
    )

    def supports_file(self, path: Path) -> bool:
        if path.suffix not in (".js", ".ts", ".mjs"):
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return "fastify" in content.lower() or "require('fastify')" in content
        except OSError:
            return False

    def parse(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        if path.is_dir():
            for file in path.rglob("*"):
                if self.supports_file(file):
                    routes.extend(self._parse_file(file))
        elif self.supports_file(path):
            routes.extend(self._parse_file(path))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return routes

        for match in self.ROUTE_RE.finditer(content):
            method = match.group(1).upper()
            route_path = match.group(2)
            routes.append(RouteEntry(
                method=method,
                path=route_path,
                source=str(path),
            ))

        for match in self.ROUTE_OBJ_RE.finditer(content):
            block = match.group(1)
            method_m = self.ROUTE_OBJ_METHOD_RE.search(block)
            url_m = self.ROUTE_OBJ_URL_RE.search(block)
            if method_m and url_m:
                routes.append(RouteEntry(
                    method=method_m.group(1).upper(),
                    path=url_m.group(1),
                    source=str(path),
                ))

        return routes
