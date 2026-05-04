from pathlib import Path

import yaml
from typer.testing import CliRunner

from doc2md.cli import app
from tests.conftest import FIXTURES


def test_full_pipeline_extracts_images_renders_table_and_index(tmp_path: Path) -> None:
    output = tmp_path / "out.md"
    result = CliRunner().invoke(app, [str(FIXTURES / "sample_digital.pdf"), "-o", str(output)])

    assert result.exit_code == 0, result.output
    assert output.exists()
    assert list((tmp_path / "images").glob("fig*_page3.*"))

    content = output.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(content.split("---", 2)[1])
    assert frontmatter["schema_version"] == "1.0"

    assert "| Quarter | Revenue | Growth | Notes |" in content
    assert "![Figure 1 -" in content
    assert "](images/fig1_page3." in content
    assert "## Document Index" in content
    assert "### Pages" in content
    assert "### Tables" in content
    assert "### Figures" in content


def test_mixed_pdf_pipeline_combines_digital_and_ocr_content(tmp_path: Path) -> None:
    output = tmp_path / "mixed.md"
    result = CliRunner().invoke(
        app,
        [
            str(FIXTURES / "sample_mixed.pdf"),
            "-o",
            str(output),
            "--ocr-engine",
            "direct",
            "--ocr-lang",
            "eng",
        ],
    )

    assert result.exit_code == 0, result.output
    content = output.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(content.split("---", 2)[1])

    assert frontmatter["document_type"] == "mixed"
    assert frontmatter["ocr_applied"] is True
    assert "Sample Digital PDF" in content
    assert "Introduction" in content
