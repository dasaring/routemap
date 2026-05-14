import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


class AspParser(BaseParser):
    """Parser for ASP.NET Core minimal API and controller-based routes in C# files."""

    # Minimal API: app.MapGet("/path", ...)
    MINIMAL_PATTERN = re.compile(
        r'app\.Map(Get|Post|Put|Delete|Patch|Methods)\s*\(\s*["\']([^"\']+)["\']',
        re.IGNORECASE,
    )

    # Attribute routing: [HttpGet("/path")] or [Route("/path")]
    ATTRIBUTE_PATTERN = re.compile(
        r'\[(Http(Get|Post|Put|Delete|Patch)|Route)\s*\(\s*["\']([^"\']+)["\']\s*\)\]',
        re.IGNORECASE,
    )

    # Route prefix from [Route("api/[controller]")]
    CONTROLLER_ROUTE_PATTERN = re.compile(
        r'\[Route\s*\(\s*["\']([^"\']+)["\']\s*\)\]',
        re.IGNORECASE,
    )

    def supports_file(self, path: Path) -> bool:
        if path.suffix.lower() != ".cs":
            return False
        content = path.read_text(errors="ignore")
        return (
            "app.Map" in content
            or "[HttpGet" in content
            or "[HttpPost" in content
            or "[HttpPut" in content
            or "[HttpDelete" in content
            or "[HttpPatch" in content
        )

    def parse(self, root: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        for cs_file in root.rglob("*.cs"):
            if self.supports_file(cs_file):
                routes.extend(self._parse_file(cs_file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        content = path.read_text(errors="ignore")
        source = str(path)

        # Minimal API routes
        for match in self.MINIMAL_PATTERN.finditer(content):
            method = match.group(1).upper()
            route_path = match.group(2)
            if method == "METHODS":
                method = "ANY"
            routes.append(RouteEntry(method=method, path=route_path, source=source))

        # Attribute-based routes — detect controller prefix
        controller_prefix = ""
        prefix_match = self.CONTROLLER_ROUTE_PATTERN.search(content)
        if prefix_match:
            controller_prefix = prefix_match.group(1).rstrip("/")

        for match in self.ATTRIBUTE_PATTERN.finditer(content):
            verb_or_route = match.group(1).upper()
            if verb_or_route == "ROUTE":
                continue  # skip bare [Route] — it's a prefix, not an endpoint
            method = match.group(2).upper() if match.group(2) else "GET"
            action_path = match.group(3).lstrip("/")
            full_path = f"/{controller_prefix}/{action_path}".replace("//", "/")
            routes.append(RouteEntry(method=method, path=full_path, source=source))

        return routes
