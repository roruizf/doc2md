import contextlib
import io
import logging
import time
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import fitz
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from doc2md.config import Settings
from doc2md.core.base_converter import BaseConverter
from doc2md.core.document import Frontmatter, IndexEntry, MarkdownDocument, Page
from doc2md.core.exceptions import LockedDocument
from doc2md.rendering.table_renderer import render_table

LOGGER = logging.getLogger(__name__)


class PdfDigitalConverter(BaseConverter):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.fallback_used = False

    def convert(self, input_path: Path) -> MarkdownDocument:
        page_count = _page_count_or_raise_locked(input_path)
        self.fallback_used = False
        try:
            return self._convert_with_docling(input_path, page_count)
        except Exception as exc:
            self.fallback_used = True
            LOGGER.warning(
                "Docling failed while converting %s (%s); falling back to PyMuPDF raw extraction. "
                "Next step: rerun with --verbose for details or inspect the source PDF.",
                input_path,
                exc,
            )
            return self._convert_with_pymupdf(input_path, page_count)

    def _convert_with_docling(self, input_path: Path, page_count: int) -> MarkdownDocument:
        started_at = time.perf_counter()
        converter = _docling_converter()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            result = converter.convert(input_path)
        LOGGER.debug("Docling converted %s in %.2fs", input_path, time.perf_counter() - started_at)

        docling_doc = result.document
        pages, index_entries = _pages_from_docling(docling_doc, page_count)
        _append_figure_entries(input_path, index_entries)
        return MarkdownDocument(
            frontmatter=_frontmatter(input_path, pages, self.settings),
            pages=pages,
            index_entries=index_entries,
        )

    def _convert_with_pymupdf(self, input_path: Path, page_count: int) -> MarkdownDocument:
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

        if len(pages) != page_count:
            LOGGER.debug("PyMuPDF page count changed from %s to %s", page_count, len(pages))
        return MarkdownDocument(
            frontmatter=_frontmatter(input_path, pages, self.settings),
            pages=pages,
            index_entries=index_entries,
        )


@lru_cache(maxsize=1)
def _docling_converter() -> DocumentConverter:
    options = PdfPipelineOptions(
        do_ocr=False,
        accelerator_options=AcceleratorOptions(num_threads=2, device=AcceleratorDevice.CPU),
    )
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )


def _page_count_or_raise_locked(input_path: Path) -> int:
    with fitz.open(input_path) as pdf:
        if pdf.is_encrypted:
            raise LockedDocument(
                f"PDF is encrypted: {input_path}. Next step: provide --password."
            )
        return len(pdf)


def _frontmatter(input_path: Path, pages: list[Page], settings: Settings) -> Frontmatter:
    return Frontmatter(
        schema_version="1.0",
        title=input_path.stem,
        source_file=input_path.name,
        format="pdf",
        page_count=len(pages),
        date_converted=datetime.now().astimezone().isoformat(),
        document_type="digital",
        language=None,
        ocr_applied=False,
        images_strategy=settings.images_strategy,
        converter_version=settings.converter_version,
    )


def _pages_from_docling(docling_doc: Any, page_count: int) -> tuple[list[Page], list[IndexEntry]]:
    page_parts: dict[int, list[str]] = {page_number: [] for page_number in range(1, page_count + 1)}
    index_entries = [
        IndexEntry(kind="page", label=f"Page {page_number}", anchor_id=f"page-{page_number}")
        for page_number in range(1, page_count + 1)
    ]
    table_ranges = _table_ranges_by_page(docling_doc)
    title_ref = _title_ref(docling_doc)

    for item in getattr(docling_doc, "texts", []):
        page_number = _item_page_number(item)
        text = str(getattr(item, "text", "")).strip()
        if page_number is None or not text or page_number not in page_parts:
            continue
        if _item_inside_table(item, table_ranges.get(page_number, [])):
            continue

        if _is_section_header(item):
            if getattr(item, "self_ref", None) == title_ref:
                rendered = f"# {text}"
            else:
                rendered = f"{_heading_prefix(item)} {text}"
            index_entries.append(
                IndexEntry(kind="section", label=text, anchor_id=f"page-{page_number}")
            )
        else:
            rendered = text
        page_parts[page_number].append(rendered)

    table_number = 1
    for table in getattr(docling_doc, "tables", []):
        page_number = _item_page_number(table)
        if page_number is None or page_number not in page_parts:
            continue
        headers, rows = _table_to_rows(table)
        if headers:
            page_parts[page_number].append(render_table(headers, rows))
            index_entries.append(
                IndexEntry(
                    kind="table",
                    label=f"Table {table_number}",
                    anchor_id=f"page-{page_number}",
                )
            )
            table_number += 1

    pages = [
        Page(number=page_number, anchor_id=f"page-{page_number}", content="\n\n".join(parts))
        for page_number, parts in page_parts.items()
    ]
    return pages, index_entries


def _title_ref(docling_doc: Any) -> str | None:
    first_page_headers = [
        item
        for item in getattr(docling_doc, "texts", [])
        if _is_section_header(item) and _item_page_number(item) == 1
    ]
    if not first_page_headers:
        return None
    topmost = max(first_page_headers, key=lambda item: _bbox_top(item) or 0.0)
    return getattr(topmost, "self_ref", None)


def _bbox_top(item: Any) -> float | None:
    prov = getattr(item, "prov", None) or []
    if not prov:
        return None
    bbox = getattr(prov[0], "bbox", None)
    return float(getattr(bbox, "t", 0.0)) if bbox is not None else None


def _is_section_header(item: Any) -> bool:
    return str(getattr(item, "label", "")).endswith("section_header")


def _heading_prefix(item: Any) -> str:
    level = int(getattr(item, "level", 1) or 1)
    markdown_level = min(max(level + 1, 2), 6)
    return "#" * markdown_level


def _item_page_number(item: Any) -> int | None:
    prov = getattr(item, "prov", None) or []
    if not prov:
        return None
    page_number = getattr(prov[0], "page_no", None)
    return int(page_number) if page_number is not None else None


def _table_ranges_by_page(docling_doc: Any) -> dict[int, list[Any]]:
    ranges: dict[int, list[Any]] = {}
    for table in getattr(docling_doc, "tables", []):
        page_number = _item_page_number(table)
        prov = getattr(table, "prov", None) or []
        if page_number is not None and prov:
            ranges.setdefault(page_number, []).append(getattr(prov[0], "bbox", None))
    return ranges


def _item_inside_table(item: Any, table_bboxes: list[Any]) -> bool:
    prov = getattr(item, "prov", None) or []
    if not prov:
        return False
    bbox = getattr(prov[0], "bbox", None)
    if bbox is None:
        return False
    return any(
        _bbox_inside(bbox, table_bbox)
        for table_bbox in table_bboxes
        if table_bbox is not None
    )


def _bbox_inside(inner: Any, outer: Any) -> bool:
    return (
        float(getattr(inner, "l", 0.0)) >= float(getattr(outer, "l", 0.0))
        and float(getattr(inner, "r", 0.0)) <= float(getattr(outer, "r", 0.0))
        and float(getattr(inner, "b", 0.0)) >= float(getattr(outer, "b", 0.0))
        and float(getattr(inner, "t", 0.0)) <= float(getattr(outer, "t", 0.0))
    )


def _table_to_rows(table: Any) -> tuple[list[str], list[list[str]]]:
    grid = getattr(getattr(table, "data", None), "grid", None)
    if not grid:
        return [], []

    rows = [[str(getattr(cell, "text", "") or "") for cell in row] for row in grid]
    rows = [_dedupe_spanned_cells(row) for row in rows]
    if rows and len(set(rows[0])) == 1 and len(rows) > 1:
        rows = rows[1:]
    if not rows:
        return [], []
    return rows[0], rows[1:]


def _dedupe_spanned_cells(row: list[str]) -> list[str]:
    deduped: list[str] = []
    for cell in row:
        if deduped and cell == deduped[-1]:
            continue
        deduped.append(cell)
    return deduped


def _append_figure_entries(input_path: Path, index_entries: list[IndexEntry]) -> None:
    figure_number = 1
    with fitz.open(input_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            for _image_info in page.get_images(full=True):
                index_entries.append(
                    IndexEntry(
                        kind="figure",
                        label=f"Figure {figure_number}",
                        anchor_id=f"page-{page_number}",
                    )
                )
                figure_number += 1


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
