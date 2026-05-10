from dataclasses import dataclass

import pytesseract
from PIL import Image


@dataclass(frozen=True)
class OcrImageResult:
    text: str
    mean_confidence: float
    min_confidence: float | None
    word_count: int


def ocr_image(image: Image.Image, lang: str) -> tuple[str, float]:
    result = ocr_image_result(image, lang)
    return result.text, result.mean_confidence


def ocr_image_result(image: Image.Image, lang: str) -> OcrImageResult:
    data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
    confidences = _confidence_values(data.get("conf", []))
    text_parts = [
        text.strip()
        for text in data.get("text", [])
        if isinstance(text, str) and text.strip()
    ]
    mean_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    min_confidence = min(confidences) if confidences else None
    return OcrImageResult(
        text=" ".join(text_parts),
        mean_confidence=mean_confidence,
        min_confidence=min_confidence,
        word_count=len(text_parts),
    )


def _confidence_values(values: list[object]) -> list[float]:
    confidences: list[float] = []
    for value in values:
        try:
            confidence = float(str(value))
        except (TypeError, ValueError):
            continue
        if confidence >= 0:
            confidences.append(confidence)
    return confidences
