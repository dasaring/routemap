from typing import List
from routemap.parsers.base import RouteEntry

METHOD_COLORS = {
    "GET": "\033[92m",
    "POST": "\033[94m",
    "PUT": "\033[93m",
    "PATCH": "\033[95m",
    "DELETE": "\033[91m",
}
RESET = "\033[0m"
BOLD = "\033[1m"


class AsciiRenderer:
    """Renders a list of RouteEntry objects as a formatted ASCII route map."""

    def __init__(self, use_color: bool = True):
        self.use_color = use_color

    def _colorize(self, text: str, color: str) -> str:
        if self.use_color:
            return f"{color}{text}{RESET}"
        return text

    def _format_method(self, method: str) -> str:
        color = METHOD_COLORS.get(method.upper(), "")
        padded = method.upper().ljust(7)
        return self._colorize(padded, color)

    def _group_by_source(self, routes: List[RouteEntry]) -> dict:
        groups: dict = {}
        for route in routes:
            source = route.source_file or "unknown"
            groups.setdefault(source, []).append(route)
        return groups

    def render(self, routes: List[RouteEntry]) -> str:
        if not routes:
            return "No routes found."

        lines = []
        header = self._colorize("ROUTEMAP — API Route Map", BOLD)
        lines.append(header)
        lines.append("=" * 50)

        groups = self._group_by_source(routes)
        for source, group_routes in sorted(groups.items()):
            lines.append(f"\n  {self._colorize(source, BOLD)}")
            lines.append("  " + "-" * 46)
            for route in sorted(group_routes, key=lambda r: r.path):
                method_str = self._format_method(route.method)
                handler = f"  → {route.handler}" if route.handler else ""
                lines.append(f"  {method_str}  {route.path}{handler}")

        lines.append("\n" + "=" * 50)
        lines.append(f"  Total routes: {len(routes)}")
        return "\n".join(lines)

    def render_to_file(self, routes: List[RouteEntry], output_path: str) -> None:
        """Write rendered output (without ANSI codes) to a text file."""
        original = self.use_color
        self.use_color = False
        content = self.render(routes)
        self.use_color = original
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content + "\n")
