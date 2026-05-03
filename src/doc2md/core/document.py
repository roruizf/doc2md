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

