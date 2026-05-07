from typing import List
from routemap.parsers.base import RouteEntry

METHOD_COLORS = {
    "GET": "#61affe",
    "POST": "#49cc90",
    "PUT": "#fca130",
    "PATCH": "#50e3c2",
    "DELETE": "#f93e3e",
    "HEAD": "#9012fe",
    "OPTIONS": "#0d5aa7",
}
DEFAULT_COLOR = "#aaaaaa"


class SvgRenderer:
    """Renders route maps as SVG diagrams."""

    ROW_HEIGHT = 36
    PADDING = 20
    METHOD_BOX_W = 72
    METHOD_BOX_H = 22
    PATH_X = 120
    FONT = "monospace"

    def __init__(self, title: str = "API Route Map"):
        self.title = title

    def render(self, routes: List[RouteEntry]) -> str:
        if not routes:
            return self._wrap("", width=400, height=60)

        groups = self._group_by_source(routes)
        lines = []
        y = self.PADDING + 30  # leave room for title

        for source, entries in groups.items():
            # Section header
            lines.append(
                f'  <text x="{self.PADDING}" y="{y}" '
                f'font-family="{self.FONT}" font-size="13" '
                f'font-weight="bold" fill="#333">{self._escape(source)}</text>'
            )
            y += self.ROW_HEIGHT - 8

            for entry in entries:
                color = METHOD_COLORS.get(entry.method.upper(), DEFAULT_COLOR)
                # Method badge
                lines.append(
                    f'  <rect x="{self.PADDING}" y="{y - 16}" '
                    f'width="{self.METHOD_BOX_W}" height="{self.METHOD_BOX_H}" '
                    f'rx="4" fill="{color}"/>'
                )
                lines.append(
                    f'  <text x="{self.PADDING + self.METHOD_BOX_W // 2}" y="{y - 1}" '
                    f'font-family="{self.FONT}" font-size="11" fill="white" '
                    f'text-anchor="middle">{self._escape(entry.method.upper())}</text>'
                )
                # Path text
                label = self._escape(entry.path)
                if entry.handler:
                    label += f" ({self._escape(entry.handler)})"
                lines.append(
                    f'  <text x="{self.PATH_X}" y="{y - 1}" '
                    f'font-family="{self.FONT}" font-size="12" fill="#222">{label}</text>'
                )
                y += self.ROW_HEIGHT

            y += 8  # extra gap between groups

        total_height = y + self.PADDING
        total_width = 700
        return self._wrap("\n".join(lines), width=total_width, height=total_height)

    def _wrap(self, body: str, width: int, height: int) -> str:
        title_el = (
            f'  <text x="{width // 2}" y="22" font-family="{self.FONT}" '
            f'font-size="15" font-weight="bold" fill="#111" text-anchor="middle">'
            f'{self._escape(self.title)}</text>'
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
            f'  <rect width="{width}" height="{height}" fill="#fafafa"/>\n'
            f"{title_el}\n"
            f"{body}\n"
            f"</svg>"
        )

    def _group_by_source(self, routes: List[RouteEntry]):
        groups: dict = {}
        for r in routes:
            groups.setdefault(r.source_file or "unknown", []).append(r)
        return groups

    @staticmethod
    def _escape(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
