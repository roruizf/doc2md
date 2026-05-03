import pytest
from pydantic import ValidationError

from doc2md.core.document import Frontmatter


def valid_frontmatter_kwargs() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "title": "Sample",
        "source_file": "sample.pdf",
        "format": "pdf",
        "page_count": 1,
        "date_converted": "2026-05-03T20:00:00+07:00",
        "document_type": "digital",
        "language": None,
        "ocr_applied": False,
        "images_strategy": "placeholder",
        "converter_version": "0.1.0",
    }


def test_frontmatter_accepts_schema_version_1_0() -> None:
    frontmatter = Frontmatter(**valid_frontmatter_kwargs())

    assert frontmatter.schema_version == "1.0"


def test_frontmatter_rejects_other_schema_version() -> None:
    kwargs = valid_frontmatter_kwargs()
    kwargs["schema_version"] = "2.0"

    with pytest.raises(ValidationError):
        Frontmatter(**kwargs)

