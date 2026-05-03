from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImageMeta:
    figure_number: int
    description: str
    output_path: Path
    page_number: int


def apply_strategy(strategy: str, image_meta: ImageMeta) -> str:
    if strategy == "placeholder":
        return (
            f"![Figure {image_meta.figure_number} - {image_meta.description}]"
            f"({image_meta.output_path.as_posix()})"
        )
    if strategy == "omit":
        return f"[IMAGE OMITTED: Figure {image_meta.figure_number}]"
    if strategy == "vlm":
        raise NotImplementedError("VLM strategy lands in P10")
    raise ValueError(f"Unknown image strategy: {strategy}")

