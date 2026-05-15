import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


class NextJSParser(BaseParser):
    """Parser for Next.js App Router and Pages Router API routes."""

    # Pages Router: pages/api/**/*.{js,ts}
    # App Router: app/**/route.{js,ts}
    _PAGES_API_RE = re.compile(r"pages[\\/]api[\\/]")
    _APP_ROUTE_RE = re.compile(r"app[\\/].*route\.(js|ts)$")

    # export async function GET(...) / export function POST(...)
    _HANDLER_RE = re.compile(
        r"export\s+(?:async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s*\(",
        re.MULTILINE,
    )

    # Pages Router default export handler (all methods)
    _DEFAULT_EXPORT_RE = re.compile(
        r"export\s+default\s+(?:async\s+)?function", re.MULTILINE
    )

    def supports_file(self, path: str) -> bool:
        p = Path(path)
        if p.suffix not in (".js", ".ts", ".jsx", ".tsx"):
            return False
        parts = p.as_posix()
        return bool(
            self._PAGES_API_RE.search(parts) or self._APP_ROUTE_RE.search(parts)
        )

    def parse(self, directory: str) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        root = Path(directory)
        for ext in ("*.js", "*.ts", "*.jsx", "*.tsx"):
            for file in root.rglob(ext):
                if self.supports_file(str(file)):
                    routes.extend(self._parse_file(file, root))
        return routes

    def _parse_file(self, file: Path, root: Path) -> List[RouteEntry]:
        try:
            content = file.read_text(encoding="utf-8")
        except OSError:
            return []

        route_path = self._derive_route_path(file, root)
        rel = file.as_posix()
        source = str(file.relative_to(root))
        routes: List[RouteEntry] = []

        if self._APP_ROUTE_RE.search(rel):
            # App Router — explicit HTTP method exports
            for match in self._HANDLER_RE.finditer(content):
                method = match.group(1).upper()
                routes.append(
                    RouteEntry(method=method, path=route_path, source=source)
                )
        else:
            # Pages Router — default export handles all methods
            if self._DEFAULT_EXPORT_RE.search(content):
                for method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                    routes.append(
                        RouteEntry(method=method, path=route_path, source=source)
                    )

        return routes

    def _derive_route_path(self, file: Path, root: Path) -> str:
        rel = file.relative_to(root).as_posix()

        # App Router: strip leading 'app/' and trailing '/route.{ext}'
        if self._APP_ROUTE_RE.search(rel):
            rel = re.sub(r"^app/", "", rel)
            rel = re.sub(r"/route\.(js|ts|jsx|tsx)$", "", rel)
        else:
            # Pages Router: strip leading 'pages/api/' and extension
            rel = re.sub(r"^pages/api/", "", rel)
            rel = re.sub(r"\.(js|ts|jsx|tsx)$", "", rel)
            if rel == "index":
                rel = ""

        # Convert [param] -> :param
        rel = re.sub(r"\[([^\]]+)\]", r":\1", rel)
        return "/" + rel if not rel.startswith("/") else rel
