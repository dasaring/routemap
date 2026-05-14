import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


class HapiParser(BaseParser):
    """
    Parser for Hapi.js route definitions.

    Supports patterns like:
        server.route({ method: 'GET', path: '/users', handler: ... })
        server.route([{ method: 'POST', path: '/users', ... }])
        server.route({ method: ['GET', 'POST'], path: '/items', ... })
    """

    # Match server.route({ ... }) blocks (single or array)
    _ROUTE_RE = re.compile(
        r"server\.route\s*\(",
        re.MULTILINE,
    )

    # Extract method and path from a route object literal
    _METHOD_RE = re.compile(
        r"method\s*:\s*(?:'([A-Z]+)'|\[([^\]]+)\])",
        re.IGNORECASE,
    )
    _PATH_RE = re.compile(
        r"path\s*:\s*['\"]([^'\"]+)['\"]",
    )

    def supports_file(self, path: Path) -> bool:
        if path.suffix not in (".js", ".ts"):
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return "server.route" in content and (
                "@hapi/hapi" in content or "require('hapi')" in content
                or 'require("hapi")' in content or "from 'hapi'" in content
                or 'from "hapi"' in content or "from '@hapi/hapi'" in content
                or 'from "@hapi/hapi"' in content
            )
        except OSError:
            return False

    def parse(self, root: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        for path in root.rglob("*"):
            if path.is_file() and self.supports_file(path):
                routes.extend(self._parse_file(path))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return routes

        # Find each server.route( call and grab the brace-delimited block
        for match in self._ROUTE_RE.finditer(content):
            start = match.end()
            block = self._extract_block(content, start)
            if not block:
                continue
            routes.extend(self._extract_routes(block, path))
        return routes

    def _extract_block(self, content: str, start: int) -> str:
        """Extract balanced braces/brackets starting at `start`."""
        depth = 0
        i = start
        while i < len(content):
            if content[i] in "{[":
                depth += 1
            elif content[i] in "}]":
                depth -= 1
                if depth == 0:
                    return content[start : i + 1]
            i += 1
        return ""

    def _extract_routes(self, block: str, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        path_match = self._PATH_RE.search(block)
        method_match = self._METHOD_RE.search(block)
        if not path_match or not method_match:
            return routes

        route_path = path_match.group(1)

        if method_match.group(1):
            methods = [method_match.group(1).upper()]
        else:
            raw = method_match.group(2)
            methods = [m.strip().strip("'\"'").upper() for m in raw.split(",")]

        for method in methods:
            routes.append(
                RouteEntry(method=method, path=route_path, source=str(path))
            )
        return routes
