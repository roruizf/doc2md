from doc2md.config import Settings
from doc2md.converters.pdf_scanned import PdfScannedConverter
from tests.conftest import FIXTURES


def test_convert_sample_scanned_pdf_marks_ocr_metadata() -> None:
    doc = PdfScannedConverter().convert(FIXTURES / "sample_scanned.pdf")

    assert doc.frontmatter.document_type == "scanned"
    assert doc.frontmatter.ocr_applied is True
    assert doc.frontmatter.language is not None
    assert any(page.content.strip() for page in doc.pages)


def test_convert_sample_scanned_pdf_with_direct_engine() -> None:
    doc = PdfScannedConverter(Settings(ocr_engine="direct", ocr_lang="eng")).convert(
        FIXTURES / "sample_scanned.pdf"
    )

    assert doc.frontmatter.document_type == "scanned"
    assert doc.frontmatter.ocr_applied is True
    assert doc.frontmatter.language == "en"
    assert doc.frontmatter.ocr_confidence_mean is not None
    assert doc.frontmatter.ocr_confidence_min is not None
    assert doc.frontmatter.ocr_low_confidence_pages is not None
    assert doc.frontmatter.ocr_text_chars is not None
    assert doc.frontmatter.ocr_text_chars > 0
    assert doc.frontmatter.ocr_text_chars_per_page is not None
    assert doc.frontmatter.ocr_suspicious_char_ratio is not None
    assert doc.frontmatter.ocr_language_requested == "eng"
    assert doc.frontmatter.ocr_language_used == "eng"
    assert doc.frontmatter.ocr_language_fallback_used is False
    assert doc.frontmatter.ocr_degraded_conditions is not None
    assert any("Sample" in page.content or "Digital" in page.content for page in doc.pages)
