from doc2md.core.document import Frontmatter, IndexEntry, MarkdownDocument, Page
from doc2md.core.validator import validate
from tests.unit.test_frontmatter import valid_frontmatter_kwargs


def make_doc(
    frontmatter: Frontmatter | None = None,
    pages: list[Page] | None = None,
    index_entries: list[IndexEntry] | None = None,
) -> MarkdownDocument:
    return MarkdownDocument(
        frontmatter=frontmatter or Frontmatter(**valid_frontmatter_kwargs()),
        pages=pages if pages is not None else [Page(number=1, anchor_id="page-1", content="Text")],
        index_entries=index_entries if index_entries is not None else [],
    )


def test_valid_doc_returns_valid_with_no_warnings() -> None:
    result = validate(make_doc())

    assert result.valid is True
    assert result.warnings == []


def test_missing_required_field_returns_warning() -> None:
    frontmatter = Frontmatter.model_construct(**valid_frontmatter_kwargs())
    frontmatter.title = ""

    result = validate(make_doc(frontmatter=frontmatter))

    assert result.valid is False
    assert any("title" in warning for warning in result.warnings)


def test_page_count_mismatch_returns_warning() -> None:
    frontmatter = Frontmatter(**{**valid_frontmatter_kwargs(), "page_count": 3})
    pages = [
        Page(number=1, anchor_id="page-1", content="One"),
        Page(number=2, anchor_id="page-2", content="Two"),
    ]

    result = validate(make_doc(frontmatter=frontmatter, pages=pages))

    assert result.valid is False
    assert any("Page numbers" in warning for warning in result.warnings)


def test_missing_index_anchor_returns_warning() -> None:
    index_entries = [IndexEntry(kind="figure", label="Figure 1", anchor_id="figure-1")]

    result = validate(make_doc(index_entries=index_entries))

    assert result.valid is False
    assert any("figure-1" in warning for warning in result.warnings)

