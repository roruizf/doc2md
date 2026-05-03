from datetime import datetime
from pathlib import Path

import fitz

from doc2md.config import Settings
from doc2md.core.base_converter import BaseConverter
from doc2md.core.document import Frontmatter, MarkdownDocument, Page


class PdfDigitalConverter(BaseConverter):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def convert(self, input_path: Path) -> MarkdownDocument:
        with fitz.open(input_path) as pdf:
            pages = [
                Page(
                    number=page_number,
                    anchor_id=f"page-{page_number}",
                    content=page.get_text("text"),
                )
                for page_number, page in enumerate(pdf, start=1)
            ]

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
        return MarkdownDocument(frontmatter=frontmatter, pages=pages, index_entries=[])
