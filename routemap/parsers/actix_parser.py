import re
from pathlib import Path
from typing import List
from .base import BaseParser, RouteEntry


class ActixParser(BaseParser):
    """Parser for Rust Actix-web applications."""

    # Matches: .route("/path", web::get().to(handler))
    ROUTE_PATTERN = re.compile(
        r'\.route\(\s*"([^"]+)"\s*,\s*web::([a-zA-Z]+)\(\)',
        re.MULTILINE,
    )

    # Matches: #[get("/path")], #[post("/path")], etc.
    MACRO_PATTERN = re.compile(
        r'#\[(?:get|post|put|patch|delete|head|options)\("([^"]+)"\)\]\s*'
        r'(?:pub\s+)?(?:async\s+)?fn\s+(\w+)',
        re.MULTILINE,
    )

    # Matches: .service(web::scope("/prefix"))
    SCOPE_PATTERN = re.compile(
        r'web::scope\(\s*"([^"]+)"\s*\)',
        re.MULTILINE,
    )

    MACRO_METHOD_PATTERN = re.compile(
        r'#\[(get|post|put|patch|delete|head|options)\("([^"]+)"\)\]',
        re.MULTILINE,
    )

    def supports_file(self, path: Path) -> bool:
        if path.suffix != ".rs":
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return "actix_web" in content or "actix-web" in content
        except OSError:
            return False

    def parse(self, root: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        for rs_file in root.rglob("*.rs"):
            if self.supports_file(rs_file):
                routes.extend(self._parse_file(rs_file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return routes

        # Detect scope prefix (simple single-scope support)
        scope_prefix = ""
        scope_match = self.SCOPE_PATTERN.search(content)
        if scope_match:
            scope_prefix = scope_match.group(1).rstrip("/")

        # Attribute macros: #[get("/path")]
        for match in self.MACRO_METHOD_PATTERN.finditer(content):
            method = match.group(1).upper()
            path_str = scope_prefix + match.group(2)
            routes.append(
                RouteEntry(
                    method=method,
                    path=path_str,
                    handler=None,
                    source=str(path),
                )
            )

        # .route("/path", web::get()) style
        for match in self.ROUTE_PATTERN.finditer(content):
            path_str = scope_prefix + match.group(1)
            method = match.group(2).upper()
            routes.append(
                RouteEntry(
                    method=method,
                    path=path_str,
                    handler=None,
                    source=str(path),
                )
            )

        return routes
