import re
from pathlib import Path
from typing import List

from routemap.parsers.base import BaseParser, RouteEntry


class ChaliceParser(BaseParser):
    """Parser for AWS Chalice Python microframework route definitions."""

    # Matches: @app.route('/path', methods=['GET', 'POST'])
    # or:      @app.route('/path')
    ROUTE_RE = re.compile(
        r"@\w+\.route\(\s*['\"]([^'\"]+)['\"]\s*(?:,\s*methods\s*=\s*\[([^\]]+)\])?\s*\)",
        re.MULTILINE,
    )

    def supports_file(self, path: Path) -> bool:
        if path.suffix != ".py":
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return "chalice" in content.lower() and (
                "Chalice(" in content or "from chalice" in content or "import chalice" in content
            )
        except OSError:
            return False

    def parse(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        if path.is_dir():
            for py_file in sorted(path.rglob("*.py")):
                if self.supports_file(py_file):
                    routes.extend(self._parse_file(py_file))
        elif path.is_file() and self.supports_file(path):
            routes.extend(self._parse_file(path))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return routes

        for match in self.ROUTE_RE.finditer(content):
            route_path = match.group(1)
            methods_raw = match.group(2)
            if methods_raw:
                methods = [
                    m.strip().strip("'\"")
                    for m in methods_raw.split(",")
                    if m.strip().strip("'\"")
                ]
            else:
                methods = ["GET"]

            for method in methods:
                routes.append(
                    RouteEntry(
                        method=method.upper(),
                        path=route_path,
                        source=str(path),
                    )
                )
        return routes
