from collections.abc import Iterable
from dataclasses import dataclass, field

from doc2md.core.document import Page


@dataclass(frozen=True)
class OcrQualityPage:
    page_number: int
    text: str
    confidence: float | None
    min_confidence: float | None = None
    requested_language: str | None = None
    used_language: str | None = None
    language_fallback_used: bool = False
    degraded_conditions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class OcrQualitySummary:
    confidence_mean: float | None
    confidence_min: float | None
    low_confidence_pages: int | None
    text_chars: int
    text_chars_per_page: float
    suspicious_char_ratio: float
    language_requested: str | None
    language_used: str | None
    language_fallback_used: bool
    degraded_conditions: list[str]


LOW_CONFIDENCE_THRESHOLD = 70.0
LOW_TEXT_CHARS_PER_PAGE = 25.0
COMMON_PUNCTUATION = set(".,;:!?¡¿'\"()[]{}<>-/\\|@#$%&*+=_`~^°0123456789")
KNOWN_SUSPICIOUS_CHARS = set("�□■▯")


def summarize_ocr_quality(
    pages: list[Page],
    quality_pages: list[OcrQualityPage],
) -> OcrQualitySummary:
    if quality_pages:
        combined_text = "\n".join(quality_page.text for quality_page in quality_pages)
        page_count = len(quality_pages)
    else:
        combined_text = "\n".join(page.content for page in pages)
        page_count = len(pages)
    page_count = max(page_count, 1)
    text_chars = len(combined_text.strip())
    text_chars_per_page = round(text_chars / page_count, 2)

    confidences = [
        quality_page.confidence
        for quality_page in quality_pages
        if quality_page.confidence is not None
    ]
    min_confidences = [
        quality_page.min_confidence
        for quality_page in quality_pages
        if quality_page.min_confidence is not None
    ]
    confidence_mean = round(sum(confidences) / len(confidences), 2) if confidences else None
    confidence_min = round(min(min_confidences), 2) if min_confidences else None
    low_confidence_pages = (
        sum(confidence < LOW_CONFIDENCE_THRESHOLD for confidence in confidences)
        if confidences
        else None
    )

    degraded_conditions = _degraded_conditions(
        quality_pages,
        confidence_mean,
        text_chars_per_page,
        combined_text,
    )
    return OcrQualitySummary(
        confidence_mean=confidence_mean,
        confidence_min=confidence_min,
        low_confidence_pages=low_confidence_pages,
        text_chars=text_chars,
        text_chars_per_page=text_chars_per_page,
        suspicious_char_ratio=suspicious_char_ratio(combined_text),
        language_requested=_first_value(page.requested_language for page in quality_pages),
        language_used=_first_value(page.used_language for page in quality_pages),
        language_fallback_used=any(page.language_fallback_used for page in quality_pages),
        degraded_conditions=degraded_conditions,
    )


def suspicious_char_ratio(text: str) -> float:
    nonspace_chars = [char for char in text if not char.isspace()]
    if not nonspace_chars:
        return 0.0
    suspicious = sum(1 for char in nonspace_chars if _is_suspicious_char(char))
    return round(suspicious / len(nonspace_chars), 4)


def _is_suspicious_char(char: str) -> bool:
    if char in KNOWN_SUSPICIOUS_CHARS:
        return True
    if char.isalnum() or char.isspace() or char in COMMON_PUNCTUATION:
        return False
    return not char.isprintable()


def _degraded_conditions(
    quality_pages: list[OcrQualityPage],
    confidence_mean: float | None,
    text_chars_per_page: float,
    combined_text: str,
) -> list[str]:
    conditions: set[str] = set()
    for page in quality_pages:
        conditions.update(page.degraded_conditions)
    if confidence_mean is None:
        conditions.add("ocr_confidence_unavailable")
    elif confidence_mean < LOW_CONFIDENCE_THRESHOLD:
        conditions.add("low_mean_confidence")
    if text_chars_per_page < LOW_TEXT_CHARS_PER_PAGE:
        conditions.add("low_text_density")
    if suspicious_char_ratio(combined_text) > 0.05:
        conditions.add("high_suspicious_character_ratio")
    if any(page.language_fallback_used for page in quality_pages):
        conditions.add("ocr_language_fallback_used")
    return sorted(conditions)


def _first_value(values: Iterable[str | None]) -> str | None:
    for value in values:
        if isinstance(value, str) and value:
            return value
    return None
