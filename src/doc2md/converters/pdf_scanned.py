import contextlib
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import fitz
import pytesseract
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from PIL import Image

from doc2md.config import Settings
from doc2md.core.base_converter import BaseConverter
from doc2md.core.document import Frontmatter, IndexEntry, MarkdownDocument, Page
from doc2md.ocr.tesseract_runner import ocr_image
from doc2md.utils.text_heuristics import detect_language

LOGGER = logging.getLogger(__name__)
LOW_CONFIDENCE_THRESHOLD = 70.0

TESSERACT_TO_ISO = {
    "eng": "en",
    "spa": "es",
    "fra": "fr",
    "deu": "de",
    "por": "pt",
    "ita": "it",
}
ISO_TO_TESSERACT = {value: key for key, value in TESSERACT_TO_ISO.items()}


class PdfScannedConverter(BaseConverter):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.fallback_used = False

    def convert(self, input_path: Path) -> MarkdownDocument:
        ocr_lang, language = resolve_ocr_language(input_path, self.settings.ocr_lang)
        if self.settings.ocr_engine == "direct":
            return self.convert_direct(input_path, ocr_lang, language)

        try:
            doc = self.convert_docling(input_path, language)
        except Exception as exc:
            self.fallback_used = True
            LOGGER.warning("Docling OCR failed (%s), falling back to direct Tesseract OCR", exc)
            return self.convert_direct(input_path, ocr_lang, language)

        if not any(page.content.strip() for page in doc.pages):
            self.fallback_used = True
            LOGGER.warning("Docling OCR produced no text, falling back to direct Tesseract OCR")
            return self.convert_direct(input_path, ocr_lang, language)
        return doc

    def convert_docling(self, input_path: Path, language: str | None) -> MarkdownDocument:
        from doc2md.converters.pdf_digital import _pages_from_docling

        options = PdfPipelineOptions(
            do_ocr=True,
            document_timeout=60,
            accelerator_options=AcceleratorOptions(num_threads=2, device=AcceleratorDevice.CPU),
        )
        converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
        )
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            result = converter.convert(input_path)

        page_count = _page_count(input_path)
        pages, index_entries = _pages_from_docling(result.document, page_count)
        return MarkdownDocument(
            frontmatter=scanned_frontmatter(input_path, pages, self.settings, "scanned", language),
            pages=pages,
            index_entries=index_entries,
        )

    def convert_direct(
        self,
        input_path: Path,
        ocr_lang: str | None = None,
        language: str | None = None,
        page_numbers: set[int] | None = None,
    ) -> MarkdownDocument:
        resolved_ocr_lang = ocr_lang or resolve_ocr_language(input_path, self.settings.ocr_lang)[0]
        resolved_language = language or _iso_language(resolved_ocr_lang)
        pages: list[Page] = []
        index_entries: list[IndexEntry] = []

        with fitz.open(input_path) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                if page_numbers is not None and page_number not in page_numbers:
                    continue
                text, confidence = ocr_pdf_page(page, resolved_ocr_lang)
                if confidence < LOW_CONFIDENCE_THRESHOLD:
                    LOGGER.warning("Low OCR confidence on page %s: %.1f%%", page_number, confidence)
                page_anchor = f"page-{page_number}"
                pages.append(Page(number=page_number, anchor_id=page_anchor, content=text))
                index_entries.append(
                    IndexEntry(kind="page", label=f"Page {page_number}", anchor_id=page_anchor)
                )

        return MarkdownDocument(
            frontmatter=scanned_frontmatter(
                input_path,
                pages,
                self.settings,
                "scanned",
                resolved_language,
            ),
            pages=pages,
            index_entries=index_entries,
        )


def resolve_ocr_language(pdf_path: Path, requested_lang: str | None) -> tuple[str, str | None]:
    if requested_lang:
        return requested_lang, _iso_language(requested_lang)

    with fitz.open(pdf_path) as pdf:
        if len(pdf) == 0:
            return "eng", None
        sample_text, _confidence = ocr_pdf_page(pdf[0], "eng")
    detected_language = detect_language(sample_text) or "en"
    return ISO_TO_TESSERACT.get(detected_language, "eng"), detected_language


def ocr_pdf_page(page: Any, lang: str) -> tuple[str, float]:
    pixmap = page.get_pixmap(dpi=300, alpha=False)
    image = Image.open(io.BytesIO(pixmap.tobytes("png")))
    try:
        return ocr_image(image, lang)
    except pytesseract.TesseractError:
        if lang == "eng":
            raise
        LOGGER.warning("Tesseract language '%s' failed, retrying with 'eng'", lang)
        return ocr_image(image, "eng")


def scanned_frontmatter(
    input_path: Path,
    pages: list[Page],
    settings: Settings,
    document_type: Literal["scanned", "mixed"],
    language: str | None,
) -> Frontmatter:
    return Frontmatter(
        schema_version="1.0",
        title=input_path.stem,
        source_file=input_path.name,
        format="pdf",
        page_count=len(pages),
        date_converted=datetime.now().astimezone().isoformat(),
        document_type=document_type,
        language=language,
        ocr_applied=True,
        images_strategy=settings.images_strategy,
        converter_version=settings.converter_version,
    )


def _page_count(input_path: Path) -> int:
    with fitz.open(input_path) as pdf:
        return len(pdf)


def _iso_language(ocr_lang: str) -> str | None:
    if len(ocr_lang) == 2:
        return ocr_lang
    return TESSERACT_TO_ISO.get(ocr_lang)
