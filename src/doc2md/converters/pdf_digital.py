import contextlib
import io
from datetime import datetime
from pathlib import Path

import fitz

from doc2md.config import Settings
from doc2md.core.base_converter import BaseConverter
from doc2md.core.document import Frontmatter, IndexEntry, MarkdownDocument, Page
from doc2md.rendering.table_renderer import render_table


class PdfDigitalConverter(BaseConverter):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def convert(self, input_path: Path) -> MarkdownDocument:
        with fitz.open(input_path) as pdf:
            pages: list[Page] = []
            index_entries: list[IndexEntry] = []
            table_number = 1
            figure_number = 1

            for page_number, page in enumerate(pdf, start=1):
                page_anchor = f"page-{page_number}"
                content = page.get_text("text")
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

        frontmatter = Frontmatter(
            schema_version="1.0",
            title=input_path.stem,
            source_file=input_path.name,
            format="pdf",
            page_count=len(pages),
            date_converted=datetime.now().astimezone().isoformat(),
            document_type="digital",
            language=None,
            ocr_applied=False,
            images_strategy=self.settings.images_strategy,
            converter_version=self.settings.converter_version,
        )
        return MarkdownDocument(frontmatter=frontmatter, pages=pages, index_entries=index_entries)


def _find_tables(page: fitz.Page) -> list[tuple[list[str], list[list[str]]]]:
    if not hasattr(page, "find_tables"):
        return []

    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        table_finder = page.find_tables()
    tables: list[tuple[list[str], list[list[str]]]] = []
    for table in table_finder.tables:
        extracted = table.extract()
        if not extracted:
            continue
        headers = [str(cell or "") for cell in extracted[0]]
        rows = [[str(cell or "") for cell in row] for row in extracted[1:]]
        tables.append((headers, rows))
    return tables
