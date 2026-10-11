from enum import StrEnum

class LayoutFormat(StrEnum):
    DOT = "dot"
    FDP = "fdp"
    NEATO = "neato"
    TREE = "tree"

class OutputFormat(StrEnum):
    GRAPHVIZ = "graphviz"
    MERMAID = "mermaid"
    TEXT = "text"
