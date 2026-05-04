from pathlib import Path

from doc2md.config import Settings
from doc2md.converters import docx as docx_module
from doc2md.converters.docx import DocxConverter
from tests.conftest import FIXTURES


def test_convert_sample_docx_preserves_headings_table_images_and_sections(tmp_path: Path) -> None:
    converter = DocxConverter()
    doc = converter.convert(FIXTURES / "sample.docx")
    images = converter.extract_images(FIXTURES / "sample.docx", tmp_path)
    content = "\n\n".join(page.content for page in doc.pages)

    assert doc.frontmatter.document_type == "docx"
    assert doc.frontmatter.page_count == 2
    assert [page.anchor_id for page in doc.pages] == ["page-1", "page-2"]
    assert "# Sample Document" in content
    assert "## Data Table" in content
    assert "| R1C1 | R1C2 | R1C3 |" in content
    assert images
    assert list((tmp_path / "images").glob("fig*_page1.*"))


def test_convert_sample_docx_with_images_omit_extracts_no_images(tmp_path: Path) -> None:
    converter = DocxConverter(Settings(images_strategy="omit"))
    doc = converter.convert(FIXTURES / "sample.docx")
    images = converter.extract_images(FIXTURES / "sample.docx", tmp_path)

    assert doc.frontmatter.images_strategy == "omit"
    assert images == []
    assert not (tmp_path / "images").exists()


def test_docx_docling_failure_falls_back_to_python_docx(
    monkeypatch,
) -> None:
    class FailingDocumentConverter:
        def convert(self, _input_path: object) -> object:
            raise RuntimeError("docling boom")

    monkeypatch.setattr(docx_module, "DocumentConverter", lambda: FailingDocumentConverter())
    converter = DocxConverter()

    doc = converter.convert(FIXTURES / "sample.docx")

    assert converter.docling_failed is True
    assert doc.frontmatter.document_type == "docx"
    assert any("Sample Document" in page.content for page in doc.pages)

