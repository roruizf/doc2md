from pathlib import Path

import yaml
from typer.testing import CliRunner

from doc2md.cli import app
from tests.conftest import FIXTURES


def test_cli_single_file_writes_markdown_with_valid_frontmatter(tmp_path: Path) -> None:
    output = tmp_path / "out.md"
    result = CliRunner().invoke(app, [str(FIXTURES / "sample_digital.pdf"), "-o", str(output)])

    assert result.exit_code == 0, result.output
    assert output.exists()

    content = output.read_text(encoding="utf-8")
    assert 'schema_version: "1.0"' in content
    assert '<a id="page-1"></a>' in content

    frontmatter_text = content.split("---", 2)[1]
    frontmatter = yaml.safe_load(frontmatter_text)
    assert frontmatter["schema_version"] == "1.0"
    assert frontmatter["format"] == "pdf"
    assert frontmatter["page_count"] == 3
    assert frontmatter["document_type"] == "digital"
    assert frontmatter["ocr_applied"] is False

