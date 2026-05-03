from dataclasses import dataclass
from pathlib import Path
from typing import Any

import fitz

from doc2md.images.naming import image_filename


@dataclass(frozen=True)
class ExtractedImage:
    figure_number: int
    page_number: int
    path: Path
    ext: str
    width: int
    height: int


def extract_images_from_pdf(pdf_path: Path, output_dir: Path) -> list[ExtractedImage]:
    image_dir = output_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    extracted: list[ExtractedImage] = []
    figure_number = 1

    with fitz.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            for image_info in page.get_images(full=True):
                xref = image_info[0]
                image_data: dict[str, Any] = doc.extract_image(xref)
                ext = str(image_data.get("ext", "png"))
                filename = image_filename(figure_number, page_number, ext)
                path = image_dir / filename
                path.write_bytes(image_data["image"])
                extracted.append(
                    ExtractedImage(
                        figure_number=figure_number,
                        page_number=page_number,
                        path=path,
                        ext=ext,
                        width=int(image_data.get("width", 0)),
                        height=int(image_data.get("height", 0)),
                    )
                )
                figure_number += 1

    return extracted

