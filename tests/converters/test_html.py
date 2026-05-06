from pathlib import Path

import yaml

from doc2md.config import Settings
from doc2md.converters import html as html_module
from doc2md.converters.html import HtmlConverter
from doc2md.core import pipeline
from tests.conftest import FIXTURES


def test_convert_sample_html_preserves_headings_table_and_image(tmp_path: Path) -> None:
    converter = HtmlConverter()
    doc = converter.convert(FIXTURES / "sample.html")
    images = converter.extract_images(FIXTURES / "sample.html", tmp_path)

    assert doc.frontmatter.document_type == "html"
    assert doc.frontmatter.page_count is None
    assert "# Sample HTML Document" in doc.pages[0].content
    assert "| Name | Value | Note |" in doc.pages[0].content
    assert images
    assert list((tmp_path / "images").glob("fig1_page1.png"))


def test_html_bs4_fallback_produces_schema_compliant_markdown(
    monkeypatch,
) -> None:
    class FailingMarkItDown:
        def convert_local(self, _path: object) -> object:
            raise RuntimeError("markitdown boom")

    monkeypatch.setattr(html_module, "MarkItDown", lambda: FailingMarkItDown())

    doc = HtmlConverter().convert(FIXTURES / "sample.html")

    assert doc.frontmatter.title == "Sample HTML"
    assert doc.frontmatter.document_type == "html"
    assert "# Sample HTML Document" in doc.pages[0].content
    assert "| Name | Value | Note |" in doc.pages[0].content


def test_html_pipeline_renders_schema_compliant_markdown(tmp_path: Path) -> None:
    output = tmp_path / "out.md"

    pipeline.run(FIXTURES / "sample.html", output, Settings())

    content = output.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(content.split("---", 2)[1])
    assert frontmatter["format"] == "html"
    assert frontmatter["document_type"] == "html"
    assert '<a id="page-1"></a>' in content
    assert "](images/fig1_page1.png)" in content
