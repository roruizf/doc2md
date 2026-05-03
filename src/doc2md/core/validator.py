import re
from dataclasses import dataclass
from pathlib import Path

from doc2md.core.document import MarkdownDocument

NULLABLE_FRONTMATTER_FIELDS = {"page_count", "language"}


@dataclass
class ValidationResult:
    valid: bool
    warnings: list[str]


def validate(
    doc: MarkdownDocument,
    rendered_markdown: str | None = None,
    output_path: Path | None = None,
) -> ValidationResult:
    warnings: list[str] = []
    warnings.extend(_frontmatter_warnings(doc))
    warnings.extend(_page_sequence_warnings(doc))
    warnings.extend(_index_anchor_warnings(doc))
    if rendered_markdown is not None and output_path is not None:
        warnings.extend(_image_reference_warnings(rendered_markdown, output_path))
    return ValidationResult(valid=len(warnings) == 0, warnings=warnings)


def _frontmatter_warnings(doc: MarkdownDocument) -> list[str]:
    warnings: list[str] = []
    for field_name in type(doc.frontmatter).model_fields:
        value = getattr(doc.frontmatter, field_name, None)
        if field_name in NULLABLE_FRONTMATTER_FIELDS:
            continue
        if value is None or value == "":
            warnings.append(f"Frontmatter field '{field_name}' is required")
    return warnings


def _page_sequence_warnings(doc: MarkdownDocument) -> list[str]:
    page_count = doc.frontmatter.page_count
    if page_count is None:
        return []

    expected_numbers = list(range(1, page_count + 1))
    actual_numbers = [page.number for page in doc.pages]
    if actual_numbers != expected_numbers:
        return [f"Page numbers must be sequential 1..{page_count}; got {actual_numbers}"]
    return []


def _index_anchor_warnings(doc: MarkdownDocument) -> list[str]:
    known_anchor_ids = {page.anchor_id for page in doc.pages}
    known_anchor_ids.update(_section_anchor_ids(doc))
    warnings: list[str] = []
    for entry in doc.index_entries:
        if entry.anchor_id not in known_anchor_ids:
            warnings.append(
                f"Index entry '{entry.label}' references missing anchor '{entry.anchor_id}'"
            )
    return warnings


def _section_anchor_ids(doc: MarkdownDocument) -> set[str]:
    section_entries = (entry for entry in doc.index_entries if entry.kind == "section")
    return {
        entry.anchor_id
        for entry in section_entries
        if _page_contains_anchor(doc, entry.anchor_id)
    }


def _page_contains_anchor(doc: MarkdownDocument, anchor_id: str) -> bool:
    anchor_markup = f'id="{anchor_id}"'
    return any(anchor_markup in page.content for page in doc.pages)


def _image_reference_warnings(rendered_markdown: str, output_path: Path) -> list[str]:
    warnings: list[str] = []
    image_paths = re.findall(r"!\[[^\]]*]\(([^)]+)\)", rendered_markdown)
    for image_path in image_paths:
        candidate = output_path.parent / image_path
        if not candidate.exists():
            warnings.append(f"Image reference does not exist: {image_path}")
    return warnings
