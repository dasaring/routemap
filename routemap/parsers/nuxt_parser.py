import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


class NuxtParser(BaseParser):
    """
    Parser for Nuxt.js applications.
    Supports both Nuxt 2 (pages/) and Nuxt 3 (server/api/) file-based routing.
    """

    # Nuxt 3 server/api route handlers
    _METHOD_RE = re.compile(
        r"export\s+default\s+defineEventHandler|defineEventHandler|eventHandler",
        re.IGNORECASE,
    )
    _EXPLICIT_METHOD_RE = re.compile(
        r"export\s+default\s+define(Get|Post|Put|Patch|Delete|Head)EventHandler",
        re.IGNORECASE,
    )

    def supports_file(self, path: Path) -> bool:
        parts = path.parts
        suffix = path.suffix
        if suffix not in (".js", ".ts", ".vue"):
            return False
        # pages/ directory (Nuxt 2/3 page routing)
        if "pages" in parts and suffix in (".vue", ".js", ".ts"):
            return True
        # server/api/ directory (Nuxt 3 API routes)
        if "server" in parts and "api" in parts:
            return True
        return False

    def parse(self, root: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        for path in root.rglob("*"):
            if path.is_file() and self.supports_file(path):
                routes.extend(self._parse_file(path, root))
        return routes

    def _parse_file(self, path: Path, root: Path) -> List[RouteEntry]:
        parts = path.parts
        rel = path.relative_to(root)

        if "server" in parts and "api" in parts:
            return self._parse_api_file(path, rel)
        elif "pages" in parts:
            return self._parse_page_file(path, rel)
        return []

    def _parse_api_file(self, path: Path, rel: Path) -> List[RouteEntry]:
        content = path.read_text(encoding="utf-8", errors="ignore")
        route_path = self._derive_api_path(rel)
        method = self._detect_method(path.stem, content)
        return [
            RouteEntry(
                method=method,
                path=route_path,
                source=str(rel),
            )
        ]

    def _parse_page_file(self, path: Path, rel: Path) -> List[RouteEntry]:
        route_path = self._derive_page_path(rel)
        return [
            RouteEntry(
                method="GET",
                path=route_path,
                source=str(rel),
            )
        ]

    def _derive_api_path(self, rel: Path) -> str:
        # e.g. server/api/users/[id].ts -> /api/users/:id
        try:
            idx = rel.parts.index("api")
            parts = list(rel.parts[idx:])
        except ValueError:
            parts = list(rel.parts)

        stem = Path(parts[-1]).stem
        # strip method suffix like .get, .post etc.
        stem = re.sub(r"\.(get|post|put|patch|delete|head)$", "", stem, flags=re.IGNORECASE)
        parts[-1] = stem if stem else "index"
        if parts[-1] == "index":
            parts = parts[:-1]
        path_str = "/" + "/".join(parts)
        path_str = re.sub(r"\[([^\]]+)\]", r":\1", path_str)
        return path_str or "/"

    def _derive_page_path(self, rel: Path) -> str:
        # e.g. pages/users/[id].vue -> /users/:id
        try:
            idx = rel.parts.index("pages")
            parts = list(rel.parts[idx + 1:])
        except ValueError:
            parts = list(rel.parts)

        if not parts:
            return "/"
        stem = Path(parts[-1]).stem
        if stem == "index":
            parts = parts[:-1]
        else:
            parts[-1] = stem
        path_str = "/" + "/".join(parts) if parts else "/"
        path_str = re.sub(r"\[([^\]]+)\]", r":\1", path_str)
        return path_str

    def _detect_method(self, stem: str, content: str) -> str:
        method_match = re.search(
            r"\.(get|post|put|patch|delete|head)$", stem, re.IGNORECASE
        )
        if method_match:
            return method_match.group(1).upper()
        explicit = self._EXPLICIT_METHOD_RE.search(content)
        if explicit:
            return explicit.group(1).upper()
        return "GET"
