
import json


def quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def walk(node):
    yield node
    for child in node.get("children", []):
        yield from walk(child)


def render_graphviz(
    architecture: dict,
    layout: str = "dot",
) -> str:
    """Generate Graphviz DOT with a selectable layout engine."""

    if layout not in {"dot", "neato", "fdp"}:
        raise ValueError(
            "Graphviz layout must be dot, neato, or fdp"
        )

    root = architecture["root"]
    nodes = list(walk(root))
    known_ids = {node["id"] for node in nodes}

    direction = architecture.get("direction", "vertical")
    rankdir = "TB" if direction == "vertical" else "LR"

    lines = [
        "digraph Architecture {",
        f"    label={quote(architecture['title'])};",
        '    labelloc="t";',
        f'    layout="{layout}";',
        f'    rankdir="{rankdir}";',
        '    node [shape=box, style="rounded"];',
    ]

    for node in nodes:
        lines.append(
            f"    {quote(node['id'])} "
            f"[label={quote(node['label'])}];"
        )

        for child in node.get("children", []):
            lines.append(
                f"    {quote(node['id'])} -> "
                f"{quote(child['id'])};"
            )

    # Add optional cross-edges.
    for edge in architecture.get("edges", []):
        source = edge["from"]
        target = edge["to"]

        if source not in known_ids or target not in known_ids:
            raise ValueError(
                f"Unknown edge endpoint: {source!r} -> {target!r}"
            )

        attributes = []
        if edge.get("label"):
            attributes.append(f"label={quote(edge['label'])}")

        suffix = (
            " [" + ", ".join(attributes) + "]"
            if attributes else ""
        )

        lines.append(
            f"    {quote(source)} -> {quote(target)}{suffix};"
        )

    lines.append("}")
    return "\n".join(lines)