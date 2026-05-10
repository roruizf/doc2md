from pathlib import Path

import yaml

from doc2md.config import Settings
from doc2md.converters.image import ImageConverter
from doc2md.core import pipeline
from tests.conftest import FIXTURES


def test_convert_sample_image_ocr_text_and_metadata(tmp_path: Path) -> None:
    converter = ImageConverter()
    doc = converter.convert(FIXTURES / "sample_image.png")
    images = converter.extract_images(FIXTURES / "sample_image.png", tmp_path)

    assert doc.frontmatter.document_type == "scanned-image"
    assert doc.frontmatter.ocr_applied is True
    assert doc.frontmatter.ocr_confidence_mean is not None
    assert doc.frontmatter.ocr_text_chars is not None
    assert doc.frontmatter.ocr_text_chars > 0
    assert doc.frontmatter.page_count == 1
    assert "Hello" in doc.pages[0].content
    assert "doc2md" in doc.pages[0].content
    assert images
    assert list((tmp_path / "images").glob("fig1_page1.png"))


def test_image_pipeline_renders_schema_compliant_markdown(tmp_path: Path) -> None:
    output = tmp_path / "out.md"

    pipeline.run(FIXTURES / "sample_image.png", output, Settings(ocr_lang="eng"))

    content = output.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(content.split("---", 2)[1])
    assert frontmatter["format"] == "image"
    assert frontmatter["document_type"] == "scanned-image"
    assert frontmatter["ocr_applied"] is True
    assert "doc2md" in content
    assert "](images/fig1_page1.png)" in content
