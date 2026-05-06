from pathlib import Path

import yaml

from doc2md.config import Settings
from doc2md.converters.epub import EpubConverter
from doc2md.core import pipeline
from tests.conftest import FIXTURES


def test_convert_sample_epub_returns_three_chapter_pages_and_metadata() -> None:
    doc = EpubConverter().convert(FIXTURES / "sample.epub")

    assert doc.frontmatter.title == "Sample EPUB"
    assert doc.frontmatter.language == "en"
    assert doc.frontmatter.document_type == "epub"
    assert doc.frontmatter.page_count == 3
    assert [page.anchor_id for page in doc.pages] == ["page-1", "page-2", "page-3"]
    assert "# Chapter 1: Introduction" in doc.pages[0].content
    assert "# Chapter 2: Data" in doc.pages[1].content
    assert "# Chapter 3: Conclusion" in doc.pages[2].content


def test_epub_extract_images_uses_standard_images_directory(tmp_path: Path) -> None:
    converter = EpubConverter()
    converter.convert(FIXTURES / "sample.epub")

    images = converter.extract_images(FIXTURES / "sample.epub", tmp_path)

    assert images
    assert images[0].page_number == 2
    assert list((tmp_path / "images").glob("fig*_page2.*"))


def test_epub_pipeline_renders_schema_compliant_markdown(tmp_path: Path) -> None:
    output = tmp_path / "out.md"

    pipeline.run(FIXTURES / "sample.epub", output, Settings())

    content = output.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(content.split("---", 2)[1])
    assert frontmatter["title"] == "Sample EPUB"
    assert frontmatter["language"] == "en"
    assert frontmatter["document_type"] == "epub"
    assert frontmatter["page_count"] == 3
    assert content.count('<a id="page-') == 3
    assert "](images/fig1_page2.png)" in content
    assert list((tmp_path / "images").glob("fig1_page2.png"))
