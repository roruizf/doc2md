from pathlib import Path

import fitz

from doc2md.config import Settings
from doc2md.converters.pdf_digital import _find_tables
from doc2md.converters.pdf_scanned import (
    ocr_pdf_page,
    resolve_ocr_language,
    scanned_frontmatter,
)
from doc2md.core.base_converter import BaseConverter
from doc2md.core.dispatcher import MEANINGFUL_TEXT_CHARS, _meaningful_char_count
from doc2md.core.document import IndexEntry, MarkdownDocument, Page
from doc2md.rendering.table_renderer import render_table


class PdfMixedConverter(BaseConverter):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def convert(self, input_path: Path) -> MarkdownDocument:
        ocr_lang, language = resolve_ocr_language(input_path, self.settings.ocr_lang)
        pages: list[Page] = []
        index_entries: list[IndexEntry] = []
        table_number = 1
        figure_number = 1

        with fitz.open(input_path) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                page_anchor = f"page-{page_number}"
                raw_text = page.get_text("text")
                if _meaningful_char_count(raw_text) >= MEANINGFUL_TEXT_CHARS:
                    content = raw_text
                    tables = _find_tables(page)
                    if tables:
                        rendered_tables = [render_table(headers, rows) for headers, rows in tables]
                        content = content.rstrip() + "\n\n" + "\n\n".join(rendered_tables) + "\n"
                        for _headers, _rows in tables:
                            index_entries.append(
                                IndexEntry(
                                    kind="table",
                                    label=f"Table {table_number}",
                                    anchor_id=page_anchor,
                                )
                            )
                            table_number += 1
                else:
                    content, _confidence = ocr_pdf_page(page, ocr_lang)

                pages.append(Page(number=page_number, anchor_id=page_anchor, content=content))
                index_entries.append(
                    IndexEntry(kind="page", label=f"Page {page_number}", anchor_id=page_anchor)
                )
                for _image_info in page.get_images(full=True):
                    index_entries.append(
                        IndexEntry(
                            kind="figure",
                            label=f"Figure {figure_number}",
                            anchor_id=page_anchor,
                        )
                    )
                    figure_number += 1

        frontmatter = scanned_frontmatter(input_path, pages, self.settings, "mixed", language)
        return MarkdownDocument(frontmatter=frontmatter, pages=pages, index_entries=index_entries)

