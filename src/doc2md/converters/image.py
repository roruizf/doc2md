import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image

from doc2md.config import Settings
from doc2md.core.base_converter import BaseConverter
from doc2md.core.document import Frontmatter, IndexEntry, MarkdownDocument, Page
from doc2md.images.extractor import ExtractedImage
from doc2md.images.naming import image_filename
from doc2md.ocr.quality import OcrQualityPage, OcrQualitySummary, summarize_ocr_quality
from doc2md.ocr.tesseract_runner import ocr_image_result


class ImageConverter(BaseConverter):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def convert(self, input_path: Path) -> MarkdownDocument:
        ocr_lang = self.settings.ocr_lang or "eng"
        with Image.open(input_path) as image:
            ocr_result = ocr_image_result(image, ocr_lang)
            text = ocr_result.text
        page = Page(number=1, anchor_id="page-1", content=text.strip())
        quality_summary = summarize_ocr_quality(
            [page],
            [
                OcrQualityPage(
                    page_number=1,
                    text=text,
                    confidence=ocr_result.mean_confidence,
                    min_confidence=ocr_result.min_confidence,
                    requested_language=ocr_lang,
                    used_language=ocr_lang,
                )
            ],
        )
        return MarkdownDocument(
            frontmatter=_frontmatter(input_path, self.settings, quality_summary),
            pages=[page],
            index_entries=[
                IndexEntry(kind="page", label="Page 1", anchor_id=page.anchor_id),
                IndexEntry(kind="figure", label="Figure 1", anchor_id=page.anchor_id),
            ],
        )

    def extract_images(self, input_path: Path, output_dir: Path) -> list[ExtractedImage]:
        if self.settings.images_strategy == "omit":
            return []

        image_dir = output_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        ext = input_path.suffix.lstrip(".") or "png"
        path = image_dir / image_filename(1, 1, ext)
        shutil.copyfile(input_path, path)
        with Image.open(input_path) as image:
            width, height = image.size
        return [
            ExtractedImage(
                figure_number=1,
                page_number=1,
                path=path,
                ext=ext,
                width=width,
                height=height,
            )
        ]


def _frontmatter(
    input_path: Path,
    settings: Settings,
    quality_summary: OcrQualitySummary,
) -> Frontmatter:
    return Frontmatter(
        schema_version="1.0",
        title=input_path.stem,
        source_file=input_path.name,
        format="image",
        page_count=1,
        date_converted=datetime.now().astimezone().isoformat(),
        document_type="scanned-image",
        language=None,
        ocr_applied=True,
        ocr_confidence_mean=quality_summary.confidence_mean,
        ocr_confidence_min=quality_summary.confidence_min,
        ocr_low_confidence_pages=quality_summary.low_confidence_pages,
        ocr_text_chars=quality_summary.text_chars,
        ocr_text_chars_per_page=quality_summary.text_chars_per_page,
        ocr_suspicious_char_ratio=quality_summary.suspicious_char_ratio,
        ocr_language_requested=quality_summary.language_requested,
        ocr_language_used=quality_summary.language_used,
        ocr_language_fallback_used=quality_summary.language_fallback_used,
        ocr_degraded_conditions=quality_summary.degraded_conditions,
        images_strategy=settings.images_strategy,
        converter_version=settings.converter_version,
    )
