from pathlib import Path

from doc2md.config import Settings
from doc2md.core.base_converter import BaseConverter
from doc2md.core.dispatcher import classify_pdf
from doc2md.core.document import MarkdownDocument
from doc2md.utils.pdf_unlock import cleanup_temp_pdf, try_decrypt


class PdfLockedConverter(BaseConverter):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.image_source_path: Path | None = None
        self._decrypted_path: Path | None = None

    def convert(self, input_path: Path) -> MarkdownDocument:
        decrypted_path = try_decrypt(input_path, self.settings.password)
        self._decrypted_path = decrypted_path if decrypted_path != input_path else None
        self.image_source_path = decrypted_path

        converter = _converter_for_decrypted_pdf(decrypted_path)
        converter.settings = self.settings
        doc = converter.convert(decrypted_path)
        doc.frontmatter.title = input_path.stem
        doc.frontmatter.source_file = input_path.name
        return doc

    def cleanup(self) -> None:
        if self._decrypted_path is not None:
            cleanup_temp_pdf(self._decrypted_path)
            self._decrypted_path = None
            self.image_source_path = None


def _converter_for_decrypted_pdf(path: Path) -> BaseConverter:
    classification = classify_pdf(path)
    if classification == "digital":
        from doc2md.converters.pdf_digital import PdfDigitalConverter

        return PdfDigitalConverter()
    if classification == "scanned":
        from doc2md.converters.pdf_scanned import PdfScannedConverter

        return PdfScannedConverter()
    from doc2md.converters.pdf_mixed import PdfMixedConverter

    return PdfMixedConverter()

