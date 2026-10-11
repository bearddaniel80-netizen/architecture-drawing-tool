
"""Generate Mermaid flowchart source from a nested architecture."""


def escape_label(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace('"', "#quot;")
        .replace("\n", "<br/>")
    )


def render_mermaid(architecture: dict) -> str:
    root = architecture["root"]
    direction = architecture.get("direction", "vertical")
    flow_direction = "TB" if direction == "vertical" else "LR"

    lines = [
        f"flowchart {flow_direction}",
        f"    %% {architecture['title']}",
    ]

    counter = 0

    def visit(node, parent=None):
        nonlocal counter

        current_id = f"node_{counter}"
        counter += 1

        label = escape_label(node["label"])
        lines.append(f'    {current_id}["{label}"]')

        if parent is not None:
            lines.append(f"    {parent} --> {current_id}")

        for child in node.get("children", []):
            visit(child, current_id)

    visit(root)
    return "\n".join(lines)