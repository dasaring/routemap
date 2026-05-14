import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


class DotNetParser(BaseParser):
    """
    Parser for ASP.NET Core minimal API and controller-based routes.
    Supports .cs files that use MapGet/MapPost/MapPut/MapDelete or
    [HttpGet]/[HttpPost]/[HttpPut]/[HttpDelete] attributes.
    """

    # Minimal API: app.MapGet("/path", handler)
    MINIMAL_PATTERN = re.compile(
        r'\.Map(Get|Post|Put|Delete|Patch)\s*\(\s*["\']([^"\']+)["\']',
        re.IGNORECASE,
    )

    # Controller attribute: [HttpGet("path")] or [HttpGet]
    ATTRIBUTE_PATTERN = re.compile(
        r'\[Http(Get|Post|Put|Delete|Patch)(?:\(\s*["\']([^"\']*)["\']\s*\))?\]',
        re.IGNORECASE,
    )

    # Route prefix on controller: [Route("api/[controller]")]
    ROUTE_PREFIX_PATTERN = re.compile(
        r'\[Route\(\s*["\']([^"\']+)["\']\s*\)\]',
        re.IGNORECASE,
    )

    def supports_file(self, path: Path) -> bool:
        if path.suffix != ".cs":
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return (
                "MapGet" in content
                or "MapPost" in content
                or "MapPut" in content
                or "MapDelete" in content
                or "[HttpGet" in content
                or "[HttpPost" in content
                or "[HttpPut" in content
                or "[HttpDelete" in content
            )
        except OSError:
            return False

    def parse(self, root: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        for cs_file in root.rglob("*.cs"):
            if self.supports_file(cs_file):
                routes.extend(self._parse_file(cs_file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        content = path.read_text(encoding="utf-8", errors="ignore")

        # Minimal API style
        for match in self.MINIMAL_PATTERN.finditer(content):
            method = match.group(1).upper()
            route_path = match.group(2)
            routes.append(RouteEntry(method=method, path=route_path, source=str(path)))

        # Controller attribute style
        if "[HttpGet" in content or "[HttpPost" in content:
            prefix_match = self.ROUTE_PREFIX_PATTERN.search(content)
            prefix = prefix_match.group(1).rstrip("/") if prefix_match else ""
            prefix = prefix.replace("[controller]", path.stem.replace("Controller", "").lower())

            for match in self.ATTRIBUTE_PATTERN.finditer(content):
                method = match.group(1).upper()
                sub = match.group(2) or ""
                full_path = f"/{prefix}/{sub}".rstrip("/") if prefix else f"/{sub}".rstrip("/")
                full_path = full_path or "/"
                routes.append(RouteEntry(method=method, path=full_path, source=str(path)))

        return routes
