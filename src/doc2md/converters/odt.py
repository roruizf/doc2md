import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pypandoc

from doc2md.config import Settings
from doc2md.core.base_converter import BaseConverter
from doc2md.core.document import Frontmatter, IndexEntry, MarkdownDocument, Page
from doc2md.core.exceptions import ConversionFailed
from doc2md.images.extractor import ExtractedImage
from doc2md.images.naming import image_filename


class OdtConverter(BaseConverter):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def convert(self, input_path: Path) -> MarkdownDocument:
        markdown = _strip_pandoc_image_refs(_pandoc_convert(input_path))
        page = Page(number=1, anchor_id="page-1", content=markdown.strip())
        return MarkdownDocument(
            frontmatter=_frontmatter(input_path, self.settings),
            pages=[page],
            index_entries=_index_entries(page),
        )

    def extract_images(self, input_path: Path, output_dir: Path) -> list[ExtractedImage]:
        if self.settings.images_strategy == "omit":
            return []

        image_dir = output_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="doc2md-odt-media-") as temp_dir:
            media_dir = Path(temp_dir)
            _pandoc_convert(input_path, extra_args=[f"--extract-media={media_dir}"])
            media_files = sorted(path for path in media_dir.rglob("*") if path.is_file())
            extracted: list[ExtractedImage] = []
            for figure_number, media_file in enumerate(media_files, start=1):
                ext = media_file.suffix.lstrip(".") or "png"
                filename = image_filename(figure_number, 1, ext)
                path = image_dir / filename
                shutil.copyfile(media_file, path)
                extracted.append(
                    ExtractedImage(
                        figure_number=figure_number,
                        page_number=1,
                        path=path,
                        ext=ext,
                        width=0,
                        height=0,
                    )
                )
            return extracted


def _pandoc_convert(input_path: Path, extra_args: list[str] | None = None) -> str:
    try:
        return str(
            pypandoc.convert_file(
                str(input_path),
                "gfm-raw_html",
                extra_args=extra_args or [],
            )
        )
    except OSError as exc:
        raise ConversionFailed("pandoc binary not found; install with apt install pandoc") from exc


def _strip_pandoc_image_refs(markdown: str) -> str:
    return re.sub(r"!\[[^\]]*]\([^)]+\)", "", markdown)


def _frontmatter(input_path: Path, settings: Settings) -> Frontmatter:
    return Frontmatter(
        schema_version="1.0",
        title=input_path.stem,
        source_file=input_path.name,
        format="odt",
        page_count=None,
        date_converted=datetime.now().astimezone().isoformat(),
        document_type="odt",
        language=None,
        ocr_applied=False,
        images_strategy=settings.images_strategy,
        converter_version=settings.converter_version,
    )


def _index_entries(page: Page) -> list[IndexEntry]:
    entries: list[IndexEntry] = []
    for line in page.content.splitlines():
        if line.startswith("#"):
            entries.append(
                IndexEntry(kind="section", label=line.lstrip("#").strip(), anchor_id=page.anchor_id)
            )
    return entries
