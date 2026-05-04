from pathlib import Path
from typing import Annotated, Literal

import typer

from doc2md.config import Settings
from doc2md.core import pipeline
from doc2md.core.exceptions import Doc2MdError
from doc2md.logging_setup import setup_logging

app = typer.Typer(add_completion=False)


@app.command()
def convert(
    input_path: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False)],
    output: Annotated[Path, typer.Option("--output", "-o")],
    images: Annotated[
        Literal["placeholder", "omit", "vlm"],
        typer.Option("--images", help="Image handling strategy for extracted document images."),
    ] = "placeholder",
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
    password: Annotated[
        str | None,
        typer.Option("--password", help="Password for encrypted PDFs."),
    ] = None,
    verbose: Annotated[bool, typer.Option("--verbose")] = False,
) -> None:
    setup_logging(verbose)
    try:
        pipeline.run(
            input_path,
            output,
            Settings(
                images_strategy=images,
                ocr_lang=ocr_lang,
                ocr_engine=ocr_engine,
                password=password,
            ),
        )
    except Doc2MdError as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(1) from exc


def main() -> None:
    app()
