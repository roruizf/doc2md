from pathlib import Path
from typing import Annotated, Literal

import typer

from doc2md.config import Settings
from doc2md.core import pipeline
from doc2md.logging_setup import setup_logging

app = typer.Typer(add_completion=False)


@app.command()
def convert(
    input_path: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False)],
    output: Annotated[Path, typer.Option("--output", "-o")],
    ocr_lang: Annotated[
        str | None,
        typer.Option(
            "--ocr-lang",
            help="Tesseract language code for OCR; omit to auto-detect from a sample page.",
        ),
    ] = None,
    ocr_engine: Annotated[
        Literal["docling", "direct"],
        typer.Option(
            "--ocr-engine",
            help=(
                "OCR engine for scanned PDFs: docling preserves layout better; "
                "direct uses raw Tesseract and is usually faster."
            ),
        ),
    ] = "docling",
    verbose: Annotated[bool, typer.Option("--verbose")] = False,
) -> None:
    setup_logging(verbose)
    pipeline.run(input_path, output, Settings(ocr_lang=ocr_lang, ocr_engine=ocr_engine))


def main() -> None:
    app()
