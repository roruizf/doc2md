import logging

import pytest

import doc2md.converters.pdf_digital as pdf_digital
from doc2md.converters.pdf_digital import PdfDigitalConverter
from doc2md.core.document import MarkdownDocument
from tests.conftest import FIXTURES


def test_convert_sample_digital_pdf_returns_three_page_markdown_document() -> None:
    doc = PdfDigitalConverter().convert(FIXTURES / "sample_digital.pdf")

    assert isinstance(doc, MarkdownDocument)
    assert len(doc.pages) == 3
    assert [page.number for page in doc.pages] == [1, 2, 3]
    assert [page.anchor_id for page in doc.pages] == ["page-1", "page-2", "page-3"]
    assert doc.frontmatter.document_type == "digital"
    assert doc.frontmatter.ocr_applied is False
    assert doc.frontmatter.format == "pdf"


def test_convert_sample_multicolumn_uses_left_column_first_order() -> None:
    doc = PdfDigitalConverter().convert(FIXTURES / "sample_multicolumn.pdf")
    content = "\n\n".join(page.content for page in doc.pages)

    assert content.index("LEFT COLUMN MARKER") < content.index("RIGHT COLUMN MARKER")


def test_docling_heading_hierarchy_is_rendered() -> None:
    doc = PdfDigitalConverter().convert(FIXTURES / "sample_digital.pdf")
    content = "\n\n".join(page.content for page in doc.pages)

    assert "# Sample Digital PDF" in content
    assert "## Introduction" in content
    assert "## Data Table" in content


def test_docling_section_index_entries_are_present() -> None:
    doc = PdfDigitalConverter().convert(FIXTURES / "sample_digital.pdf")

    section_labels = {
        entry.label for entry in doc.index_entries if entry.kind == "section"
    }
    assert {"Sample Digital PDF", "Introduction", "Data Table"}.issubset(section_labels)


def test_docling_failure_falls_back_to_pymupdf(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    class FailingConverter:
        def convert(self, _input_path: object) -> object:
            raise RuntimeError("boom")

    monkeypatch.setattr(pdf_digital, "_docling_converter", lambda: FailingConverter())
    converter = PdfDigitalConverter()

    with caplog.at_level(logging.WARNING):
        doc = converter.convert(FIXTURES / "sample_digital.pdf")

    assert converter.fallback_used is True
    assert len(doc.pages) == 3
    assert "falling back to PyMuPDF" in caplog.text


def test_fixture_without_images_still_produces_valid_markdown_document() -> None:
    doc = PdfDigitalConverter().convert(FIXTURES / "sample_multicolumn.pdf")

    assert isinstance(doc, MarkdownDocument)
    assert doc.pages
    assert all(entry.kind != "figure" for entry in doc.index_entries)
