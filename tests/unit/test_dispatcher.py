import pytest

from doc2md.converters.docx import DocxConverter
from doc2md.converters.epub import EpubConverter
from doc2md.converters.html import HtmlConverter
from doc2md.converters.image import ImageConverter
from doc2md.converters.odt import OdtConverter
from doc2md.converters.pdf_digital import PdfDigitalConverter
from doc2md.converters.pdf_locked import PdfLockedConverter
from doc2md.converters.pdf_mixed import PdfMixedConverter
from doc2md.converters.pdf_scanned import PdfScannedConverter
from doc2md.converters.txt import TxtConverter
from doc2md.core.dispatcher import classify_pdf, get_converter
from doc2md.core.exceptions import UnsupportedFormat
from tests.conftest import FIXTURES


def test_get_converter_pdf_returns_pdf_digital_converter() -> None:
    assert isinstance(get_converter("pdf"), PdfDigitalConverter)


def test_get_converter_docx_raises_unsupported_format() -> None:
    assert isinstance(get_converter("docx"), DocxConverter)


def test_get_converter_odt_returns_odt_converter() -> None:
    assert isinstance(get_converter("odt"), OdtConverter)


def test_get_converter_epub_returns_epub_converter() -> None:
    assert isinstance(get_converter("epub"), EpubConverter)


def test_get_converter_html_returns_html_converter() -> None:
    assert isinstance(get_converter("html"), HtmlConverter)


def test_get_converter_txt_returns_txt_converter() -> None:
    assert isinstance(get_converter("txt"), TxtConverter)


def test_get_converter_image_returns_image_converter() -> None:
    assert isinstance(get_converter("image"), ImageConverter)


def test_get_converter_unsupported_raises_unsupported_format() -> None:
    with pytest.raises(UnsupportedFormat):
        get_converter("unsupported")


def test_classify_pdf_returns_digital_for_sample_digital_pdf() -> None:
    assert classify_pdf(FIXTURES / "sample_digital.pdf") == "digital"


def test_classify_pdf_returns_scanned_for_sample_scanned_pdf() -> None:
    assert classify_pdf(FIXTURES / "sample_scanned.pdf") == "scanned"


def test_classify_pdf_returns_mixed_for_sample_mixed_pdf() -> None:
    assert classify_pdf(FIXTURES / "sample_mixed.pdf") == "mixed"


def test_get_converter_pdf_with_path_routes_scanned_pdf() -> None:
    assert isinstance(get_converter("pdf", FIXTURES / "sample_scanned.pdf"), PdfScannedConverter)


def test_get_converter_pdf_with_path_routes_mixed_pdf() -> None:
    assert isinstance(get_converter("pdf", FIXTURES / "sample_mixed.pdf"), PdfMixedConverter)


def test_get_converter_pdf_checks_encryption_before_classification() -> None:
    assert isinstance(get_converter("pdf", FIXTURES / "sample_locked.pdf"), PdfLockedConverter)
