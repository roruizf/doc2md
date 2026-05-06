import re
from datetime import datetime
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from typing import Any

from ebooklib import ITEM_DOCUMENT, ITEM_IMAGE, epub
from markitdown import MarkItDown

from doc2md.config import Settings
from doc2md.core.base_converter import BaseConverter
from doc2md.core.document import Frontmatter, IndexEntry, MarkdownDocument, Page
from doc2md.images.extractor import ExtractedImage
from doc2md.images.naming import image_filename


class EpubConverter(BaseConverter):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self._image_page_numbers: dict[str, int] = {}

    def convert(self, input_path: Path) -> MarkdownDocument:
        book = epub.read_epub(str(input_path))
        chapters = _spine_chapters(book)
        pages: list[Page] = []
        markitdown = MarkItDown()
        self._image_page_numbers = {}

        for chapter_index, chapter in enumerate(chapters, start=1):
            content = chapter.get_content()
            for image_ref in _image_refs(content):
                self._image_page_numbers.setdefault(image_ref, chapter_index)
            result = markitdown.convert_stream(BytesIO(content), file_extension=".html")
            markdown = _strip_markdown_image_refs(result.text_content)
            pages.append(
                Page(
                    number=chapter_index,
                    anchor_id=f"page-{chapter_index}",
                    content=markdown.strip(),
                )
            )

        return MarkdownDocument(
            frontmatter=_frontmatter(input_path, book, len(pages), self.settings),
            pages=pages,
            index_entries=_index_entries_from_pages(pages),
        )

    def extract_images(self, input_path: Path, output_dir: Path) -> list[ExtractedImage]:
        if self.settings.images_strategy == "omit":
            return []

        book = epub.read_epub(str(input_path))
        image_dir = output_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        extracted: list[ExtractedImage] = []
        for figure_number, item in enumerate(book.get_items_of_type(ITEM_IMAGE), start=1):
            item_name = str(item.get_name())
            ext = Path(item_name).suffix.lstrip(".") or _extension_from_media_type(
                str(getattr(item, "media_type", ""))
            )
            page_number = self._image_page_numbers.get(item_name, 0)
            filename = image_filename(figure_number, page_number, ext)
            path = image_dir / filename
            path.write_bytes(item.get_content())
            extracted.append(
                ExtractedImage(
                    figure_number=figure_number,
                    page_number=page_number,
                    path=path,
                    ext=ext,
                    width=0,
                    height=0,
                )
            )
        return extracted


def _spine_chapters(book: epub.EpubBook) -> list[Any]:
    documents = {
        str(item.get_id()): item
        for item in book.get_items_of_type(ITEM_DOCUMENT)
        if str(item.get_id()) != "nav"
    }
    chapters: list[Any] = []
    for spine_entry in book.spine:
        item_id = spine_entry[0] if isinstance(spine_entry, tuple) else spine_entry
        item = documents.get(str(item_id))
        if item is not None:
            chapters.append(item)
    return chapters


def _frontmatter(
    input_path: Path,
    book: epub.EpubBook,
    page_count: int,
    settings: Settings,
) -> Frontmatter:
    title = _metadata_value(book, "title")
    authors = _metadata_values(book, "creator")
    return Frontmatter(
        schema_version="1.0",
        title=title or ", ".join(authors) or input_path.stem,
        source_file=input_path.name,
        format="epub",
        page_count=page_count,
        date_converted=datetime.now().astimezone().isoformat(),
        document_type="epub",
        language=_metadata_value(book, "language"),
        ocr_applied=False,
        images_strategy=settings.images_strategy,
        converter_version=settings.converter_version,
    )


def _metadata_value(book: epub.EpubBook, name: str) -> str | None:
    values = _metadata_values(book, name)
    return values[0] if values else None


def _metadata_values(book: epub.EpubBook, name: str) -> list[str]:
    return [
        str(value).strip()
        for value, _attrs in book.get_metadata("DC", name)
        if str(value).strip()
    ]


def _index_entries_from_pages(pages: list[Page]) -> list[IndexEntry]:
    entries = [
        IndexEntry(kind="page", label=f"Page {page.number}", anchor_id=page.anchor_id)
        for page in pages
    ]
    for page in pages:
        for line in page.content.splitlines():
            if line.startswith("#"):
                entries.append(
                    IndexEntry(
                        kind="section",
                        label=line.lstrip("#").strip(),
                        anchor_id=page.anchor_id,
                    )
                )
    return entries


class _ImageRefParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "img":
            return
        for name, value in attrs:
            if name.lower() == "src" and value:
                self.refs.append(value)


def _image_refs(content: bytes) -> list[str]:
    parser = _ImageRefParser()
    parser.feed(content.decode("utf-8", errors="ignore"))
    return [_normalize_epub_ref(ref) for ref in parser.refs]


def _normalize_epub_ref(ref: str) -> str:
    return ref.split("#", 1)[0].split("?", 1)[0].lstrip("./")


def _strip_markdown_image_refs(markdown: str) -> str:
    return re.sub(r"!\[[^\]]*]\([^)]+\)", "", markdown)


def _extension_from_media_type(media_type: str) -> str:
    if "/" in media_type:
        return media_type.rsplit("/", 1)[1].replace("jpeg", "jpg")
    return "png"
