from typing import Literal

from pydantic import BaseModel


class Frontmatter(BaseModel):
    schema_version: Literal["1.0"]
    title: str
    source_file: str
    format: Literal["pdf", "docx", "odt", "epub", "html", "txt", "image"]
    page_count: int | None
    date_converted: str
    document_type: Literal[
        "digital",
        "scanned",
        "mixed",
        "scanned-image",
        "html",
        "txt",
        "epub",
        "docx",
        "odt",
    ]
    language: str | None
    ocr_applied: bool
    ocr_confidence_mean: float | None = None
    ocr_confidence_min: float | None = None
    ocr_low_confidence_pages: int | None = None
    ocr_text_chars: int | None = None
    ocr_text_chars_per_page: float | None = None
    ocr_suspicious_char_ratio: float | None = None
    ocr_language_requested: str | None = None
    ocr_language_used: str | None = None
    ocr_language_fallback_used: bool | None = None
    ocr_degraded_conditions: list[str] | None = None
    images_strategy: Literal["placeholder", "vlm", "omit"]
    converter_version: str


class IndexEntry(BaseModel):
    kind: Literal["page", "section", "table", "figure"]
    label: str
    anchor_id: str


class Page(BaseModel):
    number: int
    anchor_id: str
    content: str


class MarkdownDocument(BaseModel):
    frontmatter: Frontmatter
    pages: list[Page]
    index_entries: list[IndexEntry]
