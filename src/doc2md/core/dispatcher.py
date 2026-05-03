from doc2md.converters.pdf_digital import PdfDigitalConverter
from doc2md.core.base_converter import BaseConverter
from doc2md.core.exceptions import UnsupportedFormat


def get_converter(format: str) -> BaseConverter:
    if format == "pdf":
        return PdfDigitalConverter()
    raise UnsupportedFormat(f"Unsupported format for P1: {format}")

