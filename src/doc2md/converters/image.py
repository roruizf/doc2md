import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image

from doc2md.config import Settings
from doc2md.core.base_converter import BaseConverter
from doc2md.core.document import Frontmatter, IndexEntry, MarkdownDocument, Page
from doc2md.images.extractor import ExtractedImage
from doc2md.images.naming import image_filename
from doc2md.ocr.tesseract_runner import ocr_image


class ImageConverter(BaseConverter):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def convert(self, input_path: Path) -> MarkdownDocument:
        with Image.open(input_path) as image:
            text, _confidence = ocr_image(image, self.settings.ocr_lang or "eng")
        page = Page(number=1, anchor_id="page-1", content=text.strip())
        return MarkdownDocument(
            frontmatter=_frontmatter(input_path, self.settings),
            pages=[page],
            index_entries=[
                IndexEntry(kind="page", label="Page 1", anchor_id=page.anchor_id),
                IndexEntry(kind="figure", label="Figure 1", anchor_id=page.anchor_id),
            ],
        )

    def extract_images(self, input_path: Path, output_dir: Path) -> list[ExtractedImage]:
        if self.settings.images_strategy == "omit":
            return []

        image_dir = output_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        ext = input_path.suffix.lstrip(".") or "png"
        path = image_dir / image_filename(1, 1, ext)
        shutil.copyfile(input_path, path)
        with Image.open(input_path) as image:
            width, height = image.size
        return [
            ExtractedImage(
                figure_number=1,
                page_number=1,
                path=path,
                ext=ext,
                width=width,
                height=height,
            )
        ]


def _frontmatter(input_path: Path, settings: Settings) -> Frontmatter:
    return Frontmatter(
        schema_version="1.0",
        title=input_path.stem,
        source_file=input_path.name,
        format="image",
        page_count=1,
        date_converted=datetime.now().astimezone().isoformat(),
        document_type="scanned-image",
        language=None,
        ocr_applied=True,
        images_strategy=settings.images_strategy,
        converter_version=settings.converter_version,
    )
