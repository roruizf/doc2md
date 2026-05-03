from pathlib import Path

from doc2md.core.detector import detect_format
from tests.conftest import FIXTURES


def test_pdf_extension_on_valid_pdf_returns_pdf() -> None:
    assert detect_format(FIXTURES / "sample_digital.pdf") == "pdf"


def test_docx_extension_returns_docx() -> None:
    assert detect_format(FIXTURES / "sample.docx") == "docx"


def test_file_with_no_extension_but_pdf_mime_returns_pdf(tmp_path: Path) -> None:
    extensionless_pdf = tmp_path / "sample_digital"
    extensionless_pdf.write_bytes((FIXTURES / "sample_digital.pdf").read_bytes())

    assert detect_format(extensionless_pdf) == "pdf"


def test_unknown_extension_returns_unsupported(tmp_path: Path) -> None:
    unknown = tmp_path / "sample.unknown"
    unknown.write_text("plain text", encoding="utf-8")

    assert detect_format(unknown) == "unsupported"

