
"""Render a DiagramLayout as a Unicode text diagram."""

from ..layout import DiagramLayout, NodeLayout, ConnectorLayout


class TextRenderer:
    """Draw boxes and connectors onto a character canvas."""

    def __init__(self, padding=1):
        self.padding = padding

    def render(self, diagram: DiagramLayout) -> str:
        """Return the complete diagram as a string."""
        self.width = diagram.width + self.padding * 2
        self.height = diagram.height + self.padding * 2

        self.canvas = [
            [" "] * self.width
            for _ in range(self.height)
        ]

        # Draw connections first so box borders remain visible.
        for connector in diagram.connectors:
            self._draw_connector(connector)

        for node in diagram.nodes:
            self._draw_node(node)

        lines = [
            "".join(row).rstrip()
            for row in self.canvas
        ]

        while lines and not lines[-1]:
            lines.pop()

        return "\n".join(lines)

    def _put(self, x: int, y: int, char: str):
        """Write a character at a canvas coordinate."""
        x += self.padding
        y += self.padding

        if not (0 <= x < self.width and 0 <= y < self.height):
            return

        current = self.canvas[y][x]

        if current == " " or current == char:
            self.canvas[y][x] = char
        else:
            self.canvas[y][x] = self._merge(current, char)

    @staticmethod
    def _merge(current: str, incoming: str) -> str:
        """Merge intersecting horizontal and vertical lines."""
        if current == incoming:
            return current

        vertical = {"│", "┃", "┆", "┊"}
        horizontal = {"─", "━", "┄", "┈"}

        if current in vertical and incoming in horizontal:
            return "┼"

        if current in horizontal and incoming in vertical:
            return "┼"

        # Preserve an existing box corner or junction.
        junctions = set("┌┐└┘├┤┬┴┼")
        if current in junctions:
            return current
        if incoming in junctions:
            return incoming

        return incoming

    def _draw_node(self, node: NodeLayout):
        """Draw a rectangular node."""
        x = node.x
        y = node.y
        width = node.width
        height = node.height

        # Top and bottom borders.
        for dx in range(width):
            self._put(x + dx, y, "─")
            self._put(x + dx, y + height - 1, "─")

        # Side borders.
        for dy in range(1, height - 1):
            self._put(x, y + dy, "│")
            self._put(x + width - 1, y + dy, "│")

        # Corners.
        self._put(x, y, "┌")
        self._put(x + width - 1, y, "┐")
        self._put(x, y + height - 1, "└")
        self._put(x + width - 1, y + height - 1, "┘")

        # Center the label inside the box.
        label = node.label
        available = width - 2

        if len(label) > available:
            label = label[:available]

        label = label.center(available)
        for dx, char in enumerate(label):
            self._put(x + 1 + dx, y + 1, char)

    def _draw_connector(self, connector: ConnectorLayout):
        """Draw orthogonal connector segments and an arrow."""
        points = connector.points

        if len(points) < 2:
            return

        for index in range(len(points) - 1):
            x1, y1 = points[index]
            x2, y2 = points[index + 1]

            if x1 == x2:
                # Vertical segment.
                start, end = sorted((y1, y2))
                for y in range(start, end + 1):
                    self._put(x1, y, "│")

            elif y1 == y2:
                # Horizontal segment.
                start, end = sorted((x1, x2))
                for x in range(start, end + 1):
                    self._put(x, y1, "─")

            else:
                raise ValueError(
                    f"Connector {connector.parent_id!r} -> "
                    f"{connector.child_id!r} contains a diagonal "
                    "segment; only orthogonal routing is supported."
                )

        # Draw the arrow at the final point.
        x, y = points[-1]
        self._put(x, y, connector.arrow)


def render_text(diagram: DiagramLayout) -> str:
    """Convenience function for the CLI."""
    return TextRenderer().render(diagram)