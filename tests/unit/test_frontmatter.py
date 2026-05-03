import pytest
import yaml
from pydantic import ValidationError

from doc2md.core.document import Frontmatter
from doc2md.rendering.frontmatter import render_frontmatter


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


def test_render_frontmatter_escapes_special_chars_in_title() -> None:
    frontmatter = Frontmatter(
        **{
            **valid_frontmatter_kwargs(),
            "title": 'Sample: "quoted" document',
        }
    )

    rendered = render_frontmatter(frontmatter)
    parsed = yaml.safe_load(rendered.split("---", 2)[1])

    assert parsed["title"] == 'Sample: "quoted" document'


def test_render_frontmatter_null_page_count_serializes_as_null() -> None:
    frontmatter = Frontmatter(**{**valid_frontmatter_kwargs(), "page_count": None})

    rendered = render_frontmatter(frontmatter)
    parsed = yaml.safe_load(rendered.split("---", 2)[1])

    assert "page_count: null" in rendered
    assert parsed["page_count"] is None


def test_render_frontmatter_keeps_iso_8601_date_string() -> None:
    date_converted = "2026-05-03T21:04:09+07:00"
    frontmatter = Frontmatter(**{**valid_frontmatter_kwargs(), "date_converted": date_converted})

    rendered = render_frontmatter(frontmatter)
    parsed = yaml.safe_load(rendered.split("---", 2)[1])

    assert parsed["date_converted"] == date_converted
