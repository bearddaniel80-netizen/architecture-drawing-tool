
from pathlib import Path

import typer

from .parser import load_architecture, ArchitectureParseError
from .layout import calculate_layout
from .models import OutputFormat, LayoutFormat
from .renderers import (
    render_text, 
    render_graphviz, 
    render_mermaid
)

app = typer.Typer(
    help="Render a JSON architecture diagram.",
    no_args_is_help=True,
)


@app.command()
def main(
    input: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to the input JSON file.",
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.TEXT,
        "--format",
        "-f",
        help="Output format.",
    ),
    output: Path = typer.Option(
        Path.cwd() / "output" / "architecture.txt",
        "--output",
        "-o",
        help="Path to the output text file.",
    ),
    layout: LayoutFormat = typer.Option(
        LayoutFormat.TREE,
        "--layout",
        "-l",
        help="Layout strategy.",
    ),
):
    """Render an architecture diagram."""
    extensions = {
        "text": ".txt",
        "graphviz": ".dot",
        "mermaid": ".mmd",
    }

    output_path = output or (
        Path.cwd() / "output" / f"architecture{extensions[format]}"
    )

    try:
        architecture = load_architecture(input)

        if format == OutputFormat.GRAPHVIZ:
            graph_layout = LayoutFormat.DOT if layout == LayoutFormat.TREE else layout
            result = render_graphviz(
                architecture,
                layout=graph_layout,
            )
        elif format == OutputFormat.TEXT:
            diagram_layout = calculate_layout(architecture)
            result = render_text(diagram_layout)
        elif format == OutputFormat.MERMAID:
            result = render_mermaid(architecture)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result + "\n", encoding="utf-8")

        typer.echo(f"Diagram written to {output_path}")

    except (ArchitectureParseError, OSError, ValueError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()