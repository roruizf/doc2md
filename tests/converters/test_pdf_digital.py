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

