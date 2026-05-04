from langdetect import LangDetectException, detect


def detect_language(sample: str) -> str | None:
    if not sample.strip():
        return None
    try:
        return detect(sample)
    except LangDetectException:
        return None

