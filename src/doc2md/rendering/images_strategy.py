import logging
from dataclasses import dataclass
from pathlib import Path

from doc2md.config import Settings
from doc2md.images.vlm_client import VlmClient, VlmError

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImageMeta:
    figure_number: int
    description: str
    output_path: Path
    page_number: int
    image_path: Path | None = None


def apply_strategy(
    strategy: str,
    image_meta: ImageMeta,
    settings: Settings | None = None,
) -> str:
    if strategy == "placeholder":
        return _placeholder(image_meta, image_meta.description)
    if strategy == "omit":
        return f"[IMAGE OMITTED: Figure {image_meta.figure_number}]"
    if strategy == "vlm":
        if settings is None or image_meta.image_path is None:
            raise ValueError("VLM strategy requires settings and an image path")
        try:
            client = VlmClient(
                provider=settings.vlm_provider,
                model=settings.vlm_model or "deepseek/deepseek-vl2-small",
            )
            return _placeholder(image_meta, client.describe_image(image_meta.image_path))
        except VlmError as exc:
            LOGGER.warning(
                "VLM description failed for %s; using placeholder: %s",
                image_meta.output_path,
                exc,
            )
            return _placeholder(image_meta, image_meta.description)
    raise ValueError(f"Unknown image strategy: {strategy}")


def _placeholder(image_meta: ImageMeta, description: str) -> str:
    return (
        f"![Figure {image_meta.figure_number} - {description}]"
        f"({image_meta.output_path.as_posix()})"
    )
