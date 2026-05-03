import logging
from pathlib import Path

from doc2md.config import Settings
from doc2md.core.document import MarkdownDocument
from doc2md.images.extractor import ExtractedImage
from doc2md.rendering.frontmatter import render_frontmatter
from doc2md.rendering.images_strategy import ImageMeta, apply_strategy
from doc2md.rendering.index_builder import build_index
from doc2md.rendering.page_anchors import render_anchor
from doc2md.rendering.sanitizer import sanitize

LOGGER = logging.getLogger(__name__)


def render(
    doc: MarkdownDocument,
    output_path: Path,
    extracted_images: list[ExtractedImage],
    settings: Settings,
) -> str:
    frontmatter = render_frontmatter(doc.frontmatter)
    body_parts: list[str] = []

    for page in doc.pages:
        body_parts.append(render_anchor(page.number))
        body_parts.append("\n")
        body_parts.append(page.content.rstrip())
        page_images = [image for image in extracted_images if image.page_number == page.number]
        if page_images:
            body_parts.append("\n\n")
            rendered_images = [
                _render_image(image, output_path, settings) for image in page_images
            ]
            body_parts.append("\n\n".join(rendered_images))
        body_parts.append("\n\n")

    index = build_index(doc)
    if index:
        body_parts.append("---\n\n")
        body_parts.append(index)
        body_parts.append("\n")

    body, counts = sanitize("".join(body_parts))
    if counts:
        LOGGER.info("Sanitized replacement counts: %s", counts)
    return frontmatter + "\n" + body


def _render_image(image: ExtractedImage, output_path: Path, settings: Settings) -> str:
    image_meta = ImageMeta(
        figure_number=image.figure_number,
        description=f"Page {image.page_number} image",
        output_path=image.path.relative_to(output_path.parent),
        page_number=image.page_number,
    )
    return apply_strategy(settings.images_strategy, image_meta)
