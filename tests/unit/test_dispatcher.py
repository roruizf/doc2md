import pytest

from doc2md.converters.pdf_digital import PdfDigitalConverter
from doc2md.core.dispatcher import get_converter
from doc2md.core.exceptions import UnsupportedFormat


def test_get_converter_pdf_returns_pdf_digital_converter() -> None:
    assert isinstance(get_converter("pdf"), PdfDigitalConverter)


def test_get_converter_docx_raises_unsupported_format() -> None:
    with pytest.raises(UnsupportedFormat):
        get_converter("docx")

