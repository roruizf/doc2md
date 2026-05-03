from pathlib import Path
from typing import Annotated

import typer

from doc2md.config import Settings
from doc2md.core import pipeline
from doc2md.logging_setup import setup_logging

app = typer.Typer(add_completion=False)


@app.command()
def convert(
    input_path: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False)],
    output: Annotated[Path, typer.Option("--output", "-o")],
    verbose: Annotated[bool, typer.Option("--verbose")] = False,
) -> None:
    setup_logging(verbose)
    pipeline.run(input_path, output, Settings())


def main() -> None:
    app()

