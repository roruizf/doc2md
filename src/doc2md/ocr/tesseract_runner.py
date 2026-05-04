import pytesseract
from PIL import Image


def ocr_image(image: Image.Image, lang: str) -> tuple[str, float]:
    data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
    confidences = _confidence_values(data.get("conf", []))
    text_parts = [
        text.strip()
        for text in data.get("text", [])
        if isinstance(text, str) and text.strip()
    ]
    mean_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return " ".join(text_parts), mean_confidence


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
