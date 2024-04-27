from pathlib import Path

import exiftool
import typer
from rich import box as rich_box
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from typing_extensions import Annotated

app = typer.Typer(
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()

DISPLAYS = {
    "table": lambda f, m: metadata_table(f, m),
    "tree": lambda f, m: metadata_tree(f, m),
}


def metadata(filepath: Path, filter: str | None = None):
    """Metadata dictionary extracted with ExifTool."""
    with exiftool.ExifToolHelper() as et:
        m = et.get_metadata(filepath)[0]  # Only one file -> `[0]`
    if filter:
        m = {k: v for k, v in m.items() if filter in k}
    return m


def metadata_table(filepath, metadata):
    """Rich table displaying metadata`."""
    table = Table(
        "Field",
        "Value",
        # title=str(filepath),
        box=rich_box.ROUNDED,
    )
    for key, value in metadata.items():
        table.add_row(key, str(value))
    return table


def metadata_tree(filepath, metadata):
    """Rich tree displaying `metadata."""
    tree = Tree(f"[blue]{filepath}[blue]")
    branches = {}
    tagged_values = [(k.split(":"), v) for k, v in metadata.items()]

    for tags, value in tagged_values:
        root_tag = tags[0]

        if root_tag not in branches:
            branches[root_tag] = tree.add(f"[blue]{root_tag}[/blue]")

        if len(tags) == 2:
            branches[root_tag] = tree.add(f"[blue]{tags[1]}:[/blue] {value}")
        else:
            branches[tags[0]].add(str(value).strip())

    return tree


def display_format(value):
    if value.lower() not in DISPLAYS:
        raise typer.BadParameter(f"Format must be one of: {DISPLAYS.keys()}")
    return value


@app.command(
    help="[bold green]Display rich metadata[/bold green]",
)
def display_metadata(
    filepath: Annotated[
        Path,
        typer.Argument(
            help="Path of the file to examine",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    filter: Annotated[
        str,
        typer.Option(
            help="String to match for displaying",
        ),
    ] = None,
    display: str = typer.Option(
        default="table",
        help="How to display the metadata",
        case_sensitive=False,
        callback=display_format,
    ),
):
    displayer = DISPLAYS[display]
    meta = metadata(filepath, filter=filter)
    output = displayer(filepath, meta)
    console.print(output)


def main():
    app()


if __name__ == "__main__":
    app()
