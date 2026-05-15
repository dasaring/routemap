import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


class TRPCParser(BaseParser):
    """Parser for tRPC routers in TypeScript/JavaScript projects."""

    # Matches: publicProcedure.query / publicProcedure.mutation / router.procedure
    _PROCEDURE_RE = re.compile(
        r'(?P<name>[\w]+)\s*:\s*(?:[\w.]+\.)?(?P<type>query|mutation|subscription)\s*\(',
        re.MULTILINE,
    )
    # Matches: router({ ... }) or createRouter({ ... })
    _ROUTER_RE = re.compile(r'(?:createRouter|router)\s*\(', re.MULTILINE)
    # Matches: import.*trpc or require.*trpc
    _TRPC_IMPORT_RE = re.compile(r'(?:import|require).*["\']@trpc', re.MULTILINE)

    _METHOD_MAP = {
        "query": "GET",
        "mutation": "POST",
        "subscription": "WS",
    }

    def supports_file(self, path: Path) -> bool:
        if path.suffix not in (".ts", ".js"):
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return False
        return bool(self._TRPC_IMPORT_RE.search(content)) or "trpc" in path.name.lower()

    def parse(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        if path.is_dir():
            for file in path.rglob("*.ts"):
                routes.extend(self._parse_file(file))
            for file in path.rglob("*.js"):
                routes.extend(self._parse_file(file))
        else:
            routes.extend(self._parse_file(path))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []

        if not (self._TRPC_IMPORT_RE.search(content) or self._ROUTER_RE.search(content)):
            return []

        routes: List[RouteEntry] = []
        for match in self._PROCEDURE_RE.finditer(content):
            name = match.group("name")
            proc_type = match.group("type")
            method = self._METHOD_MAP.get(proc_type, "POST")
            route_path = f"/trpc/{name}"
            routes.append(
                RouteEntry(
                    method=method,
                    path=route_path,
                    source=str(path),
                )
            )
        return routes
