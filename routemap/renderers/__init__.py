from routemap.renderers.ascii_renderer import AsciiRenderer
from routemap.renderers.mermaid_renderer import MermaidRenderer

RENDERERS = {
    "ascii": AsciiRenderer,
    "mermaid": MermaidRenderer,
}


def get_renderer(name: str):
    """Return a renderer instance by name.

    Args:
        name: One of 'ascii' or 'mermaid'.

    Returns:
        An instantiated renderer.

    Raises:
        ValueError: If the renderer name is not recognized.
    """
    name = name.lower()
    if name not in RENDERERS:
        available = ", ".join(sorted(RENDERERS.keys()))
        raise ValueError(
            f"Unknown renderer: '{name}'. Available renderers: {available}"
        )
    return RENDERERS[name]()


__all__ = ["AsciiRenderer", "MermaidRenderer", "get_renderer", "RENDERERS"]
