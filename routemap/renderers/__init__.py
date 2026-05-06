from routemap.renderers.ascii_renderer import AsciiRenderer
from routemap.renderers.mermaid_renderer import MermaidRenderer
from routemap.renderers.json_renderer import JsonRenderer
from routemap.renderers.html_renderer import HtmlRenderer

_RENDERERS = {
    "ascii": AsciiRenderer,
    "mermaid": MermaidRenderer,
    "json": JsonRenderer,
    "html": HtmlRenderer,
}


def get_renderer(name: str):
    """Return a renderer instance by name.

    Args:
        name: One of 'ascii', 'mermaid', 'json', 'html'.

    Returns:
        An instantiated renderer.

    Raises:
        ValueError: If the renderer name is not recognised.
    """
    key = name.lower()
    if key not in _RENDERERS:
        available = ", ".join(sorted(_RENDERERS))
        raise ValueError(
            f"Unknown renderer '{name}'. Available renderers: {available}"
        )
    return _RENDERERS[key]()


def available_renderers():
    """Return a list of supported renderer names."""
    return sorted(_RENDERERS.keys())
