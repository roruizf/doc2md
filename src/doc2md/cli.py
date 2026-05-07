from pathlib import Path
from time import perf_counter
from typing import Annotated, Literal

import typer

from doc2md.config import Settings
from doc2md.core import pipeline
from doc2md.core.exceptions import Doc2MdError
from doc2md.logging_setup import setup_logging
from doc2md.utils.fs import iter_input_files, mirror_output_path
from doc2md.utils.progress import ProgressBar

app = typer.Typer(add_completion=False)


@app.command()
def convert(
    input_path: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=True)],
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
    recursive: Annotated[
        bool,
        typer.Option(
            "--recursive",
            "-r",
            help="Recursively convert supported files in a directory.",
        ),
    ] = False,
    flatten: Annotated[
        bool,
        typer.Option(
            "--flatten",
            help="Write all batch outputs directly under the output directory.",
        ),
    ] = False,
    no_progress: Annotated[
        bool,
        typer.Option("--no-progress", help="Disable progress output for batch conversion."),
    ] = False,
    verbose: Annotated[bool, typer.Option("--verbose")] = False,
) -> None:
    setup_logging(verbose)
    settings = Settings(
        images_strategy=images,
        ocr_lang=ocr_lang,
        ocr_engine=ocr_engine,
        password=password,
    )
    if input_path.is_dir():
        _convert_batch(input_path, output, settings, recursive, flatten, no_progress)
        return

    try:
        pipeline.run(input_path, output, settings)
    except Doc2MdError as exc:
        typer.secho(str(exc), err=True, fg=typer.colors.RED)
        raise typer.Exit(1) from exc


def _convert_batch(
    input_root: Path,
    output_root: Path,
    settings: Settings,
    recursive: bool,
    flatten: bool,
    no_progress: bool,
) -> None:
    start = perf_counter()
    input_files = list(iter_input_files(input_root, recursive=recursive))
    success_count = 0
    failures: list[tuple[Path, str]] = []

    progress = ProgressBar(disabled=no_progress)
    for input_file in progress.wrap(input_files, total=len(input_files), description="Converting"):
        output_path = mirror_output_path(input_root, input_file, output_root, flatten=flatten)
        try:
            pipeline.run(input_file, output_path, settings)
            success_count += 1
        except Exception as exc:  # noqa: BLE001 - batch mode isolates per-file failures.
            failures.append((input_file, str(exc)))
            typer.secho(f"Failed: {input_file}: {exc}", err=True, fg=typer.colors.RED)

    elapsed = perf_counter() - start
    fail_count = len(failures)
    typer.echo(f"{success_count} succeeded, {fail_count} failed, {elapsed:.1f}s elapsed")
    if failures:
        typer.echo("Failed files:")
        for failed_file, error in failures:
            typer.echo(f"- {failed_file}: {error}")


def main() -> None:
    app()
