import logging
from pathlib import Path

from doc2md.config import Settings
from doc2md.core.detector import detect_format
from doc2md.core.dispatcher import get_converter
from doc2md.core.validator import validate
from doc2md.images.extractor import extract_images_from_pdf
from doc2md.images.vlm_pricing import confirm_cost, estimate_cost, fetch_model_pricing
from doc2md.rendering.markdown_renderer import render

LOGGER = logging.getLogger(__name__)


def run(input_path: Path, output_path: Path, settings: Settings) -> None:
    detected_format = detect_format(input_path)
    converter = get_converter(detected_format, input_path)
    converter.settings = settings

    try:
        doc = converter.convert(input_path)
        image_source_path = getattr(converter, "image_source_path", None) or input_path
        if detected_format == "pdf":
            extracted_images = extract_images_from_pdf(image_source_path, output_path.parent)
        elif hasattr(converter, "extract_images"):
            extracted_images = converter.extract_images(input_path, output_path.parent)
        else:
            extracted_images = []
        settings = _prepare_vlm_settings(
            settings,
            doc.frontmatter.document_type,
            len(extracted_images),
        )
        markdown = render(doc, output_path, extracted_images, settings)
        result = validate(doc, rendered_markdown=markdown, output_path=output_path)
        for warning in result.warnings:
            LOGGER.warning(warning)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    finally:
        cleanup = getattr(converter, "cleanup", None)
        if callable(cleanup):
            cleanup()


def _prepare_vlm_settings(
    settings: Settings,
    document_type: str,
    image_count: int,
) -> Settings:
    if settings.images_strategy != "vlm" or image_count == 0:
        return settings

    model = settings.vlm_model or _default_vlm_model(document_type)
    vlm_settings = settings.model_copy(update={"vlm_model": model})
    try:
        estimated_cost = estimate_cost(image_count, fetch_model_pricing(model))
    except Exception as exc:  # noqa: BLE001 - pricing failure should not block conversion.
        LOGGER.warning("Could not estimate VLM cost for %s: %s", model, exc)
        return vlm_settings

    if not confirm_cost(estimated_cost, settings.vlm_cost_threshold):
        return vlm_settings.model_copy(update={"images_strategy": "placeholder"})
    return vlm_settings


def _default_vlm_model(document_type: str) -> str:
    if document_type in {"scanned", "scanned-image"}:
        return "deepseek/deepseek-ocr-2"
    return "deepseek/deepseek-vl2-small"
