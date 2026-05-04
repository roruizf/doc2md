import pytest

from doc2md.config import Settings
from doc2md.converters.pdf_locked import PdfLockedConverter
from doc2md.core.exceptions import LockedDocument
from tests.conftest import FIXTURES


def test_convert_locked_pdf_with_password_succeeds() -> None:
    doc = PdfLockedConverter(Settings(password="test123")).convert(
        FIXTURES / "sample_locked.pdf"
    )

    assert doc.frontmatter.source_file == "sample_locked.pdf"
    assert doc.frontmatter.format == "pdf"
    assert len(doc.pages) == 3
    assert any(page.content.strip() for page in doc.pages)


def test_convert_locked_pdf_without_password_raises_locked_document() -> None:
    with pytest.raises(LockedDocument, match="provide --password"):
        PdfLockedConverter().convert(FIXTURES / "sample_locked.pdf")


def test_convert_locked_pdf_with_wrong_password_raises_locked_document() -> None:
    with pytest.raises(LockedDocument, match="provide --password"):
        PdfLockedConverter(Settings(password="wrong")).convert(FIXTURES / "sample_locked.pdf")

