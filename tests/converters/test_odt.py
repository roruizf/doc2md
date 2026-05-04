from pathlib import Path

import pytest

from doc2md.converters import odt as odt_module
from doc2md.converters.odt import OdtConverter
from doc2md.core.exceptions import ConversionFailed
from tests.conftest import FIXTURES


def test_convert_sample_odt_returns_valid_markdown_document() -> None:
    doc = OdtConverter().convert(FIXTURES / "sample.odt")

    assert doc.frontmatter.document_type == "odt"
    assert doc.frontmatter.page_count is None
    assert doc.pages[0].content
    assert "Introduction" in doc.pages[0].content
    assert "Pictures/0.png" not in doc.pages[0].content


def test_odt_extract_images_with_pandoc_extract_media(tmp_path: Path) -> None:
    images = OdtConverter().extract_images(FIXTURES / "sample.odt", tmp_path)

    assert images
    assert list((tmp_path / "images").glob("fig*_page1.*"))


def test_odt_pandoc_missing_raises_conversion_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_os_error(*_args: object, **_kwargs: object) -> str:
        raise OSError("pandoc not found")

    monkeypatch.setattr(odt_module.pypandoc, "convert_file", raise_os_error)

    with pytest.raises(ConversionFailed, match="pandoc binary not found"):
        OdtConverter().convert(FIXTURES / "sample.odt")
