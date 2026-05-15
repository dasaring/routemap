import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


class FastifyTSParser(BaseParser):
    """Parser for Fastify TypeScript applications."""

    FRAMEWORK_SIGNATURES = [
        r"from ['\"]fastify['\"]" ,
        r"require\(['\"]fastify['\"]\)",
        r"import fastify",
        r"FastifyInstance",
        r"FastifyPluginAsync",
        r"FastifyPluginCallback",
    ]

    HTTP_METHODS = ["get", "post", "put", "patch", "delete", "head", "options"]

    # Matches: fastify.get('/path', ...) or server.post('/path', ...)
    ROUTE_PATTERN = re.compile(
        r"(?:fastify|app|server|router)\.(get|post|put|patch|delete|head|options)"
        r"\s*\(\s*['\"`]([^'\"` ]+)['\"`]",
        re.IGNORECASE,
    )

    # Matches: fastify.route({ method: 'GET', url: '/path' })
    ROUTE_OBJ_METHOD = re.compile(
        r"method\s*:\s*['\"`]([A-Z]+)['\"`]", re.IGNORECASE
    )
    ROUTE_OBJ_URL = re.compile(
        r"url\s*:\s*['\"`]([^'\"` ]+)['\"`]"
    )

    def supports_file(self, path: Path) -> bool:
        if path.suffix not in (".ts", ".js"):
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return False
        return any(re.search(sig, content) for sig in self.FRAMEWORK_SIGNATURES)

    def parse(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        for file in path.rglob("*") if path.is_dir() else [path]:
            if file.suffix in (".ts", ".js") and self.supports_file(file):
                routes.extend(self._parse_file(file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        content = path.read_text(encoding="utf-8", errors="ignore")
        routes: List[RouteEntry] = []

        # Chained-style: fastify.get('/path', handler)
        for match in self.ROUTE_PATTERN.finditer(content):
            method = match.group(1).upper()
            route_path = match.group(2)
            routes.append(RouteEntry(method=method, path=route_path, source=str(path)))

        # Object-style: fastify.route({ method: 'GET', url: '/path' })
        route_blocks = re.findall(
            r"\.route\s*\(\s*\{([^}]+)\}", content, re.DOTALL
        )
        for block in route_blocks:
            method_match = self.ROUTE_OBJ_METHOD.search(block)
            url_match = self.ROUTE_OBJ_URL.search(block)
            if method_match and url_match:
                method = method_match.group(1).upper()
                route_path = url_match.group(1)
                routes.append(
                    RouteEntry(method=method, path=route_path, source=str(path))
                )

        return routes
