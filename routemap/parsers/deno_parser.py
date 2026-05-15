import re
from pathlib import Path
from .base import BaseParser, RouteEntry


class DenoParser(BaseParser):
    """
    Parser for Deno (Oak framework) route definitions.

    Supports patterns like:
        router.get('/path', handler)
        router.post('/path', handler)
        new Router().get('/path', handler)
    """

    METHODS = ["get", "post", "put", "patch", "delete", "options", "head", "all"]
    ROUTE_RE = re.compile(
        r'router\s*\.\s*(' + '|'.join(METHODS) + r')\s*\(\s*[\'"]([^\'"]+)[\'"]',
        re.IGNORECASE,
    )
    OAK_IMPORT_RE = re.compile(
        r'from\s+[\'"]https?://deno\.land/x/oak|import.*oak',
        re.IGNORECASE,
    )

    def supports_file(self, path: Path) -> bool:
        if path.suffix not in (".ts", ".js"):
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return False
        return bool(self.OAK_IMPORT_RE.search(content))

    def parse(self, path: Path) -> list[RouteEntry]:
        routes: list[RouteEntry] = []
        if path.is_file():
            routes.extend(self._parse_file(path))
        elif path.is_dir():
            for file in sorted(path.rglob("*.ts")) + sorted(path.rglob("*.js")):
                if self.supports_file(file):
                    routes.extend(self._parse_file(file))
        return routes

    def _parse_file(self, path: Path) -> list[RouteEntry]:
        routes: list[RouteEntry] = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return routes
        if not self.OAK_IMPORT_RE.search(content):
            return routes
        for match in self.ROUTE_RE.finditer(content):
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
