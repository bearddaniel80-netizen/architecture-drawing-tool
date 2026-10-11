
"""Load and validate a nested JSON architecture definition."""

import json
from pathlib import Path
from typing import Any


class ArchitectureParseError(Exception):
    """Raised when an architecture file is invalid."""


def validate_node(
    node: Any,
    path: str = "root",
    seen_ids: set[str] | None = None,
) -> dict:
    """Validate and normalize a node recursively."""

    if seen_ids is None:
        seen_ids = set()

    if not isinstance(node, dict):
        raise ArchitectureParseError(
            f"{path}: expected an object"
        )

    node_id = node.get("id")
    label = node.get("label")
    children = node.get("children", [])

    if not isinstance(node_id, str) or not node_id.strip():
        raise ArchitectureParseError(
            f"{path}: 'id' must be a non-empty string"
        )

    if node_id in seen_ids:
        raise ArchitectureParseError(
            f"{path}: duplicate node id '{node_id}'"
        )

    seen_ids.add(node_id)

    if not isinstance(label, str) or not label.strip():
        raise ArchitectureParseError(
            f"{path}: 'label' must be a non-empty string"
        )

    if not isinstance(children, list):
        raise ArchitectureParseError(
            f"{path}: 'children' must be a list"
        )

    return {
        "id": node_id,
        "label": label.strip(),
        "children": [
            validate_node(
                child,
                path=f"{path}.children[{index}]",
                seen_ids=seen_ids,
            )
            for index, child in enumerate(children)
        ],
    }


def load_architecture(file_path: str | Path) -> dict:
    """Load, validate, and return an architecture definition."""

    path = Path(file_path)

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ArchitectureParseError(
            f"Invalid JSON at line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}"
        ) from exc
    except OSError as exc:
        raise ArchitectureParseError(
            f"Cannot read '{path}': {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ArchitectureParseError(
            "The document must be a JSON object"
        )

    title = data.get("title", "Architecture")
    direction = data.get("direction", "vertical")
    nodes = data.get("nodes")

    if not isinstance(title, str) or not title.strip():
        raise ArchitectureParseError(
            "'title' must be a non-empty string"
        )

    if direction not in {"vertical", "horizontal"}:
        raise ArchitectureParseError(
            "'direction' must be 'vertical' or 'horizontal'"
        )

    if not isinstance(nodes, dict) or len(nodes) != 1:
        raise ArchitectureParseError(
            "'nodes' must contain exactly one root node"
        )

    root_id, root_node = next(iter(nodes.items()))

    # Use the root's dictionary key as its ID if it is omitted.
    if isinstance(root_node, dict):
        root_node = {
            **root_node,
            "id": root_node.get("id", root_id),
        }

    normalized_root = validate_node(root_node)

    return {
        "title": title.strip(),
        "direction": direction,
        "root": normalized_root,
    }