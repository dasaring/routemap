from typing import List
from collections import defaultdict
from routemap.parsers.base import RouteEntry

METHOD_COLORS = {
    "GET": "#61affe",
    "POST": "#49cc90",
    "PUT": "#fca130",
    "PATCH": "#50e3c2",
    "DELETE": "#f93e3e",
    "OPTIONS": "#0d5aa7",
    "HEAD": "#9012fe",
}

DEFAULT_COLOR = "#999999"


class HtmlRenderer:
    """Renders route entries as a styled HTML page."""

    def __init__(self, title: str = "API Route Map"):
        self.title = title

    def render(self, routes: List[RouteEntry]) -> str:
        grouped = self._group_by_source(routes)
        sections = ""
        for source, entries in grouped.items():
            rows = ""
            for route in entries:
                color = METHOD_COLORS.get(route.method.upper(), DEFAULT_COLOR)
                rows += (
                    f'<tr>'
                    f'<td><span class="badge" style="background:{color}">{route.method.upper()}</span></td>'
                    f'<td class="path">{route.path}</td>'
                    f'<td class="handler">{route.handler or ""}</td>'
                    f'</tr>\n'
                )
            sections += (
                f'<section>'
                f'<h2>{source}</h2>'
                f'<table><thead><tr><th>Method</th><th>Path</th><th>Handler</th></tr></thead>'
                f'<tbody>{rows}</tbody></table>'
                f'</section>\n'
            )

        return (
            f'<!DOCTYPE html>\n<html lang="en">\n<head>\n'
            f'<meta charset="UTF-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'<title>{self.title}</title>\n'
            f'<style>{self._css()}</style>\n'
            f'</head>\n<body>\n'
            f'<h1>{self.title}</h1>\n'
            f'{sections}'
            f'</body>\n</html>'
        )

    def _group_by_source(self, routes: List[RouteEntry]):
        grouped = defaultdict(list)
        for route in routes:
            grouped[route.source_file].append(route)
        return grouped

    def _css(self) -> str:
        return (
            "body{font-family:sans-serif;max-width:900px;margin:40px auto;padding:0 20px;background:#fafafa;color:#333}"
            "h1{font-size:1.8em;border-bottom:2px solid #ddd;padding-bottom:8px}"
            "h2{font-size:1.1em;color:#555;margin-top:30px}"
            "table{width:100%;border-collapse:collapse;margin-bottom:20px}"
            "th{text-align:left;padding:8px 12px;background:#eee;font-size:.85em;text-transform:uppercase}"
            "td{padding:8px 12px;border-bottom:1px solid #e0e0e0;font-size:.9em}"
            ".badge{display:inline-block;padding:2px 8px;border-radius:4px;color:#fff;font-weight:bold;font-size:.8em}"
            ".path{font-family:monospace;font-size:.95em}"
            ".handler{color:#777;font-size:.85em}"
        )
