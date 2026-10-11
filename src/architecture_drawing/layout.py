
"""Calculate node and connector positions for an architecture diagram."""

from dataclasses import dataclass, field


@dataclass
class NodeLayout:
    """Geometry for one node."""
    id: str
    label: str
    x: int
    y: int
    width: int
    height: int = 3

    @property
    def center_x(self):
        return self.x + self.width // 2

    @property
    def center_y(self):
        return self.y + self.height // 2

    @property
    def right(self):
        return self.x + self.width - 1

    @property
    def bottom(self):
        return self.y + self.height - 1


@dataclass
class ConnectorLayout:
    """Geometry for a parent-to-child connection."""
    parent_id: str
    child_id: str
    points: list[tuple[int, int]] = field(default_factory=list)
    arrow: str = "▼"


@dataclass
class DiagramLayout:
    """Complete layout consumed by the renderer."""
    title: str
    direction: str
    nodes: list[NodeLayout]
    connectors: list[ConnectorLayout]
    width: int
    height: int


class LayoutEngine:
    """Convert a normalized architecture tree into diagram geometry."""

    BOX_PADDING = 2
    MIN_BOX_WIDTH = 6
    HORIZONTAL_GAP = 4
    VERTICAL_GAP = 3

    def __init__(self, direction="vertical"):
        if direction not in {"vertical", "horizontal"}:
            raise ValueError(f"Unsupported direction: {direction}")

        self.direction = direction
        self.nodes = []
        self.connectors = []

    def layout(self, architecture):
        """Calculate positions for a parsed architecture."""
        self.nodes = []
        self.connectors = []

        self.direction = architecture["direction"]
        root = architecture["root"]

        if self.direction == "vertical":
            width = self._subtree_width(root)
            self._place_vertical(root, 0, 0)
        else:
            height = self._subtree_height(root)
            self._place_horizontal(root, 0, 0)

        width = max(
            (node.right + 1 for node in self.nodes),
            default=0,
        )
        height = max(
            (node.bottom + 1 for node in self.nodes),
            default=0,
        )

        # Include connector extents in the canvas bounds.
        for connector in self.connectors:
            for x, y in connector.points:
                width = max(width, x + 1)
                height = max(height, y + 1)

        return DiagramLayout(
            title=architecture["title"],
            direction=self.direction,
            nodes=self.nodes,
            connectors=self.connectors,
            width=width,
            height=height,
        )

    def _box_width(self, node):
        return max(
            len(node["label"]) + self.BOX_PADDING * 2,
            self.MIN_BOX_WIDTH,
        )

    def _box_height(self, node):
        return 3

    def _subtree_width(self, node):
        """Width needed to fit a node and all descendants."""
        own_width = self._box_width(node)
        children = node.get("children", [])

        if not children:
            return own_width

        children_width = (
            sum(self._subtree_width(child) for child in children)
            + self.HORIZONTAL_GAP * (len(children) - 1)
        )

        return max(own_width, children_width)

    def _subtree_height(self, node):
        """Height needed to fit a node and all descendants."""
        own_height = self._box_height(node)
        children = node.get("children", [])

        if not children:
            return own_height

        children_height = (
            sum(self._subtree_height(child) for child in children)
            + self.VERTICAL_GAP * (len(children) - 1)
        )

        return max(own_height, children_height)

    def _place_vertical(self, node, left, top):
        """Place parents above their children."""
        subtree_width = self._subtree_width(node)
        box_width = self._box_width(node)
        box_height = self._box_height(node)

        x = left + (subtree_width - box_width) // 2
        current = NodeLayout(
            id=node["id"],
            label=node["label"],
            x=x,
            y=top,
            width=box_width,
            height=box_height,
        )
        self.nodes.append(current)

        children = node.get("children", [])
        if not children:
            return

        children_width = (
            sum(self._subtree_width(child) for child in children)
            + self.HORIZONTAL_GAP * (len(children) - 1)
        )

        child_left = left + (subtree_width - children_width) // 2
        child_top = top + box_height + self.VERTICAL_GAP

        child_layouts = []

        for child in children:
            before = len(self.nodes)
            self._place_vertical(child, child_left, child_top)
            child_layouts.append(self.nodes[before])
            child_left += (
                self._subtree_width(child) + self.HORIZONTAL_GAP
            )

        # Route from parent bottom to a shared horizontal branch,
        # then down to each child.
        branch_y = current.bottom + 2

        for child_layout in child_layouts:
            points = [
                (current.center_x, current.bottom + 1),
                (current.center_x, branch_y),
                (child_layout.center_x, branch_y),
                (child_layout.center_x, child_layout.y - 1),
            ]

            self.connectors.append(
                ConnectorLayout(
                    parent_id=current.id,
                    child_id=child_layout.id,
                    points=points,
                    arrow="▼",
                )
            )

    def _place_horizontal(self, node, left, top):
        """Place parents to the left of their children."""
        subtree_height = self._subtree_height(node)
        box_width = self._box_width(node)
        box_height = self._box_height(node)

        y = top + (subtree_height - box_height) // 2
        current = NodeLayout(
            id=node["id"],
            label=node["label"],
            x=left,
            y=y,
            width=box_width,
            height=box_height,
        )
        self.nodes.append(current)

        children = node.get("children", [])
        if not children:
            return

        children_height = (
            sum(self._subtree_height(child) for child in children)
            + self.VERTICAL_GAP * (len(children) - 1)
        )

        child_top = top + (subtree_height - children_height) // 2
        child_left = left + box_width + self.HORIZONTAL_GAP
        child_layouts = []

        for child in children:
            before = len(self.nodes)
            self._place_horizontal(child, child_left, child_top)
            child_layouts.append(self.nodes[before])
            child_top += (
                self._subtree_height(child) + self.VERTICAL_GAP
            )

        branch_x = current.right + 2

        for child_layout in child_layouts:
            points = [
                (current.right + 1, current.center_y),
                (branch_x, current.center_y),
                (branch_x, child_layout.center_y),
                (child_layout.x - 1, child_layout.center_y),
            ]

            self.connectors.append(
                ConnectorLayout(
                    parent_id=current.id,
                    child_id=child_layout.id,
                    points=points,
                    arrow="▶",
                )
            )


def calculate_layout(architecture):
    """Convenience function for the CLI."""
    engine = LayoutEngine(architecture["direction"])
    return engine.layout(architecture)