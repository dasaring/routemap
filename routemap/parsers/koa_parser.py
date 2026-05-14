import re
from pathlib import Path
from typing import List
from .base import BaseParser, RouteEntry


class KoaParser(BaseParser):
    """Parser for Koa.js (with koa-router) route definitions."""

    # Matches: router.get('/path', ...) or router.post('/path', ...)
    _ROUTE_RE = re.compile(
        r"(?:router|app)\.(get|post|put|patch|delete|del|head|options)"
        r"\(['\"]([^'\"]+)['\"]",
        re.IGNORECASE,
    )

    # Matches: router.use('/prefix', ...) for prefix detection
    _PREFIX_RE = re.compile(
        r"(?:router|app)\.use\(['\"]([^'\"]+)['\"]",
        re.IGNORECASE,
    )

    def supports_file(self, path: Path) -> bool:
        if path.suffix not in (".js", ".ts", ".mjs"):
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return "koa-router" in content or "@koa/router" in content
        except OSError:
            return False

    def parse(self, root: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        for ext in ("*.js", "*.ts", "*.mjs"):
            for file in root.rglob(ext):
                if self.supports_file(file):
                    routes.extend(self._parse_file(file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []

        prefix = ""
        prefix_match = self._PREFIX_RE.search(content)
        if prefix_match:
            prefix = prefix_match.group(1).rstrip("/")

        routes = []
        for match in self._ROUTE_RE.finditer(content):
            method = match.group(1).upper()
            if method == "DEL":
                method = "DELETE"
            route_path = match.group(2)
            if prefix and not route_path.startswith(prefix):
                route_path = prefix + "/" + route_path.lstrip("/")
            routes.append(
                RouteEntry(
                    method=method,
                    path=route_path,
                    source=str(path),
                )
            )
        return routes
