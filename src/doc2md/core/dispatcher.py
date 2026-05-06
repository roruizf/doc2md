from pathlib import Path
from typing import Literal

import fitz

from doc2md.core.base_converter import BaseConverter
from doc2md.core.exceptions import UnsupportedFormat
from doc2md.utils.pdf_unlock import is_encrypted

MEANINGFUL_TEXT_CHARS = 20


def get_converter(format: str, input_path: Path | None = None) -> BaseConverter:
    if format == "pdf":
        if input_path is None:
            from doc2md.converters.pdf_digital import PdfDigitalConverter

            return PdfDigitalConverter()
        if is_encrypted(input_path):
            from doc2md.converters.pdf_locked import PdfLockedConverter

            return PdfLockedConverter()
        classification = classify_pdf(input_path)
        if classification == "digital":
            from doc2md.converters.pdf_digital import PdfDigitalConverter

            return PdfDigitalConverter()
        if classification == "scanned":
            from doc2md.converters.pdf_scanned import PdfScannedConverter

            return PdfScannedConverter()
        from doc2md.converters.pdf_mixed import PdfMixedConverter

        return PdfMixedConverter()
    if format == "docx":
        from doc2md.converters.docx import DocxConverter

        return DocxConverter()
    if format == "odt":
        from doc2md.converters.odt import OdtConverter

        return OdtConverter()
    if format == "epub":
        from doc2md.converters.epub import EpubConverter

        return EpubConverter()
    raise UnsupportedFormat(f"Unsupported format: {format}")


def classify_pdf(path: Path) -> Literal["digital", "scanned", "mixed"]:
    with fitz.open(path) as pdf:
        page_count = len(pdf)
        if page_count == 0:
            return "scanned"
        meaningful_pages = sum(
            1
            for page in pdf
            if _meaningful_char_count(page.get_text("text")) >= MEANINGFUL_TEXT_CHARS
        )

    meaningful_ratio = meaningful_pages / page_count
    if meaningful_ratio == 1:
        return "digital"
    if meaningful_ratio < 0.2:
        return "scanned"
    return "mixed"


def _meaningful_char_count(text: str) -> int:
    return sum(1 for character in text if not character.isspace())
