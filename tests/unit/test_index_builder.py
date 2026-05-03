from doc2md.core.document import Frontmatter, IndexEntry, MarkdownDocument, Page
from doc2md.rendering.index_builder import build_index
from tests.unit.test_frontmatter import valid_frontmatter_kwargs


def make_doc(index_entries: list[IndexEntry]) -> MarkdownDocument:
    return MarkdownDocument(
        frontmatter=Frontmatter(**valid_frontmatter_kwargs()),
        pages=[Page(number=1, anchor_id="page-1", content="Text")],
        index_entries=index_entries,
    )


def test_empty_doc_no_index_sections_emitted() -> None:
    assert build_index(make_doc([])) == ""


def test_pages_only_index() -> None:
    index = build_index(make_doc([IndexEntry(kind="page", label="Page 1", anchor_id="page-1")]))

    assert "### Pages" in index
    assert "[Page 1](#page-1)" in index
    assert "### Tables" not in index


def test_full_doc_with_all_entry_types() -> None:
    index = build_index(
        make_doc(
            [
                IndexEntry(kind="page", label="Page 1", anchor_id="page-1"),
                IndexEntry(kind="section", label="Intro", anchor_id="page-1"),
                IndexEntry(kind="table", label="Table 1", anchor_id="page-1"),
                IndexEntry(kind="figure", label="Figure 1", anchor_id="page-1"),
            ]
        )
    )

    assert "### Pages" in index
    assert "### Sections" in index
    assert "### Tables" in index
    assert "### Figures" in index


def test_anchor_links_are_well_formed() -> None:
    index = build_index(make_doc([IndexEntry(kind="figure", label="Figure 1", anchor_id="page-1")]))

    assert "- [Figure 1](#page-1)" in index

