from pathlib import Path

import pytest

from doc2md.converters import txt as txt_module
from doc2md.converters.txt import TxtConverter
from tests.conftest import FIXTURES


def test_convert_sample_txt_infers_headings_and_language() -> None:
    doc = TxtConverter().convert(FIXTURES / "sample.txt")

    assert doc.frontmatter.document_type == "txt"
    assert doc.frontmatter.page_count is None
    assert doc.frontmatter.language == "en"
    assert "# INTRODUCTION" in doc.pages[0].content
    assert "## BACKGROUND" in doc.pages[0].content
    assert "# CONCLUSION" in doc.pages[0].content


def test_txt_low_confidence_encoding_warns_and_uses_utf8_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    input_path = tmp_path / "low-confidence.txt"
    input_path.write_bytes(b"INTRODUCTION\n===\n\nHello \xff world\n")
    monkeypatch.setattr(
        txt_module.chardet,
        "detect",
        lambda _raw: {"encoding": None, "confidence": 0.1},
    )

    doc = TxtConverter().convert(input_path)

    assert "using UTF-8 replacement" in caplog.text
    assert "Hello \ufffd world" in doc.pages[0].content
    assert doc.frontmatter.document_type == "txt"
