import logging
import re
import shutil
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify
from markitdown import MarkItDown

from doc2md.config import Settings
from doc2md.core.base_converter import BaseConverter
from doc2md.core.document import Frontmatter, IndexEntry, MarkdownDocument, Page
from doc2md.images.extractor import ExtractedImage
from doc2md.images.naming import image_filename

LOGGER = logging.getLogger(__name__)


class HtmlConverter(BaseConverter):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def convert(self, input_path: Path) -> MarkdownDocument:
        title = input_path.stem
        try:
            result = MarkItDown().convert_local(input_path)
            markdown = result.text_content
            title = result.title or title
        except Exception as exc:
            LOGGER.warning(
                "MarkItDown HTML conversion failed; using BeautifulSoup fallback: %s",
                exc,
            )
            html = input_path.read_text(encoding="utf-8", errors="replace")
            soup = BeautifulSoup(html, "html.parser")
            if soup.title and soup.title.string:
                title = soup.title.string.strip() or title
            markdown = markdownify(str(soup), heading_style="ATX")

        page = Page(
            number=1,
            anchor_id="page-1",
            content=_strip_markdown_image_refs(markdown).strip(),
        )
        return MarkdownDocument(
            frontmatter=_frontmatter(input_path, title, self.settings),
            pages=[page],
            index_entries=_index_entries(page),
        )

    def extract_images(self, input_path: Path, output_dir: Path) -> list[ExtractedImage]:
        if self.settings.images_strategy == "omit":
            return []

        html = input_path.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")
        image_dir = output_dir / "images"
        extracted: list[ExtractedImage] = []
        for figure_number, image_tag in enumerate(soup.find_all("img"), start=1):
            src = str(image_tag.get("src", "")).strip()
            if not src or _is_remote_src(src):
                continue
            source_path = (input_path.parent / _normalize_src(src)).resolve()
            if not source_path.exists():
                continue
            image_dir.mkdir(parents=True, exist_ok=True)
            ext = source_path.suffix.lstrip(".") or "png"
            path = image_dir / image_filename(figure_number, 1, ext)
            shutil.copyfile(source_path, path)
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


def _frontmatter(input_path: Path, title: str, settings: Settings) -> Frontmatter:
    return Frontmatter(
        schema_version="1.0",
        title=title,
        source_file=input_path.name,
        format="html",
        page_count=None,
        date_converted=datetime.now().astimezone().isoformat(),
        document_type="html",
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


def _strip_markdown_image_refs(markdown: str) -> str:
    return re.sub(r"!\[[^\]]*]\([^)]+\)", "", markdown)


def _is_remote_src(src: str) -> bool:
    return src.startswith(("http://", "https://", "data:"))


def _normalize_src(src: str) -> Path:
    return Path(src.split("#", 1)[0].split("?", 1)[0])
