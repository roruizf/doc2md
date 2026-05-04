import logging
from pathlib import Path

from doc2md.config import Settings
from doc2md.core.detector import detect_format
from doc2md.core.dispatcher import get_converter
from doc2md.core.validator import validate
from doc2md.images.extractor import extract_images_from_pdf
from doc2md.rendering.markdown_renderer import render

LOGGER = logging.getLogger(__name__)


def run(input_path: Path, output_path: Path, settings: Settings) -> None:
    detected_format = detect_format(input_path)
    converter = get_converter(detected_format, input_path)
    converter.settings = settings

    doc = converter.convert(input_path)
    extracted_images = (
        extract_images_from_pdf(input_path, output_path.parent) if detected_format == "pdf" else []
    )
    markdown = render(doc, output_path, extracted_images, settings)
    result = validate(doc, rendered_markdown=markdown, output_path=output_path)
    for warning in result.warnings:
        LOGGER.warning(warning)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
